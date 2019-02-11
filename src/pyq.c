#ifdef __linux__
#  ifndef _GNU_SOURCE
#    define _GNU_SOURCE
#  endif
#endif

#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#include <pwd.h>
#include <limits.h>
#ifdef __APPLE__
#  include <mach-o/dyld.h>
#  include <uuid/uuid.h>
#  include <sys/dirent.h>
#endif /* __APPLE__ */

#define TRACE if(pyq_trace) printf
static int pyq_trace;
static char progpath_buffer[PATH_MAX];

#ifdef __APPLE__
static char*
get_progpath(const char *progname)
{
    uint32_t nsexeclength = PATH_MAX;
    /* TODO: Check for error and dynamically allocate progpath. */
    _NSGetExecutablePath(progpath_buffer, &nsexeclength);
    return strdup(progpath_buffer);
}
#elif defined(__linux__) /* __APPLE__ */
#include <sched.h>
static char *
get_progpath(const char *progname)
{
    if (readlink("/proc/self/exe",
            progpath_buffer, sizeof(progpath_buffer)) == -1)
        return strdup(progname);
    return strdup(progpath_buffer);
}


static cpu_set_t cpu_set;

static int
parse_cpus(char *cpus)
{
    char *str1, *str2, *token, *subtoken;
    char *saveptr1, *saveptr2;
    int i, j, cpu[2];
    CPU_ZERO(&cpu_set);
    for (str1 = cpus; ; str1 = NULL) {
        token = strtok_r(str1, ",", &saveptr1);
        if (token == NULL)
            break;
        for (i = 0, str2 = token; ; i++, str2 = NULL) {
            subtoken = strtok_r(str2, "-", &saveptr2);
            if (subtoken != NULL) {
                cpu[i] = atoi(subtoken);
                continue;
            }
            switch (i) {
            case 1:
                CPU_SET(cpu[0], &cpu_set);
                break;
            case 2:
                for (j = cpu[0]; j <= cpu[1]; j++) {
                    CPU_SET(j, &cpu_set);
                }
                break;
            default:
                return -1;
            }
            break;
        }
    }
    return 0;
}

/* CPU_COUNT is not defined by older versions of glibc */
#ifndef CPU_COUNT
static int CPU_COUNT(cpu_set_t *set) {
  int i, count = 0;
  for (i = 0; i < CPU_SETSIZE; i++) {
    if (CPU_ISSET(i, set)) {
      count++;
    }
  }
  return count;
}
#endif /* !CPU_COUNT */

static void
print_cpus(void)
{
    int i, n;
    n = CPU_COUNT(&cpu_set);
    printf("n = %d\n", n);
    for (i = 0; i < CPU_SETSIZE; i++) {
        if (CPU_ISSET(i, &cpu_set))
            printf("%d ", i);
    }
    printf("\n");
}

static int
taskset(char *cpus)
{
    char *test_cpus;
    test_cpus = getenv("TEST_CPUS");
    if (cpus && *cpus) {
        parse_cpus(cpus);
        if (test_cpus) {
            print_cpus();
            exit(0);
        }
        /* From man sched_setaffinity:

        The argument cpusetsize is the length (in bytes) of
        the data pointed to by mask. Normally this argument
        would  be  specified  as sizeof(cpu_set_t). */
        sched_setaffinity(0, sizeof(cpu_set_t), &cpu_set);
    }
    return 0;
}
#else /* __linux__ */
    #error "Unsupported OS"
#endif

#ifndef QARCH
#error "QARCH is not set."
#endif

#define xstr(s) str(s)
#define str(s) #s


struct pyq_opts {
    char *qhome;
    char *qarch;
    char *qbin;
    char *cpus;
    union {
        struct {
            unsigned int print_qhome: 1;
            unsigned int print_qarch: 1;
            unsigned int print_qbin: 1;
            unsigned int print_cpus: 1;
        };
        unsigned int print;
    };
    unsigned int trace: 1;
    unsigned int run_q;
};

/* QHOME priority:
    1. QHOME is already set in the environment.
    2. VIRTUAL_ENV is set -> QHOME/$VIRTUAL_ENV/q
    3. Next to pyq executable
    4. ~/q
*/
int
find_q(const char* progpath, struct pyq_opts *opts, int attempt)
{
    char *qhome = opts->qhome, *prefix = NULL, *qpath = NULL, *p;
    switch (++attempt) {
        case 1:
            if (qhome) {
                attempt = 4;
                break;
            }
            ++attempt;
            /* fall through */
        case 2:
            if ((prefix = getenv("VIRTUAL_ENV"))) {
                qhome = malloc(strlen(prefix) + 3);
                strcpy(qhome, prefix);
                strcat(qhome, "/q");
                setenv("QHOME", strdup(qhome), 1);
                break;
            }
            ++attempt;
            /* fall through */
        case 3:
            p = strrchr(progpath, '/');
            if (p && (p -= 4) > progpath && !strncmp(p, "/bin/", 5)) {
                int n = p - progpath;
                qhome = calloc(1, n + 3);
                strncpy(qhome, progpath, n);
                strcat(qhome, "/q");
                setenv("QHOME", strdup(qhome), 1);
                break;
            }
            ++attempt;
            /* fall through */
        case 4:
            prefix = getenv("HOME");
            if (prefix == NULL) {
                struct passwd *pw = getpwuid(getuid());
                prefix = pw->pw_dir;
            }
            if (prefix) {
                qhome = malloc(strlen(prefix) + 3);
                strcpy(qhome, prefix);
                strcat(qhome, "/q");
                setenv("QHOME", strdup(qhome), 1);
                break;
            }
             ++attempt;
             /* fall through */
        default:
            return -1;
    }
    opts->qhome = qhome;
    TRACE("qhome = %s\n", qhome);
    opts->qbin = qpath = malloc(strlen(qhome) + strlen(opts->qarch) + 4);
    strcpy(qpath, qhome);
    strcat(strcat(strcat(qpath, "/"), opts->qarch), "/q");
    setenv("QBIN", qpath, 1);

    return attempt;
}

#define NPATHS 4


void
parse_opts(struct pyq_opts *opts, int *p_argc, char *argv[])
{
    int argc = *p_argc, i, j;
    char *p;

    memset(opts, 0, sizeof(*opts));
    for (i = 0, j = 0; i < argc; ++i) {
        if (!strncmp(argv[i], "--pyq-", 6)) {
            --(*p_argc);
            p = argv[i] + 6;
            if (!strcmp(p, "trace"))
                opts->trace = 1;
            else if (!strcmp(p, "run-q"))
                opts->run_q = 1;
            else if (!strcmp(p, "qhome"))
                opts->print_qhome = 1;
            else if (!strcmp(p, "qarch"))
                opts->print_qarch = 1;
            else if (!strcmp(p, "qbin"))
                opts->print_qbin = 1;
            else if (!strcmp(p, "cpus"))
                opts->print_cpus = 1;
            else if (!strncmp(p, "qhome=", 6))
                opts->qhome = p + 6;
            else if (!strncmp(p, "qarch=", 6))
                opts->qarch = p + 6;
            else if (!strncmp(p, "qbin=", 5))
                opts->qbin = p + 5;
            else if (!strncmp(p, "cpus=", 5))
                opts->cpus = p + 5;
            else {
                printf("unrecognized option %s\n", argv[i]);
                exit(1);
            }
        }
        else {
            argv[j++] = argv[i];
        }
    }
    /* defaults */
    if (!opts->qhome)
        opts->qhome = getenv("QHOME");
    if (!opts->qarch)
        opts->qarch = xstr(QARCH);
    if (!opts->cpus)
        opts->cpus = getenv("CPUS");
    if (!opts->cpus)
        opts->cpus = "";
}

void
exec_q(const struct pyq_opts *opts, char **args) {
    if (opts->print) {
        int i; /* NB: args ends with "-q", NULL */
        for (i = 2; args[i+1]; i+=2) {
            if (!strcmp(args[i], "QHOME="))
                args[i+1] = opts->qhome;
            if (!strcmp(args[i], "QBIN="))
                args[i+1] = opts->qbin;
        }
    }
    else if (opts->run_q) {
        ++args;
        *args = opts->qbin;
    }
    /* Flush streams before exec. */
    fflush(stdout);
    fflush(stderr);
    execvp(opts->qbin, args);
    if (errno != ENOENT)
        perror(opts->qbin);
}

static unsigned int
count_bits(unsigned int n)
{
    unsigned int count = 0;
    while (n) {
      n &= (n-1) ;
      count++;
    }
    return count;
}

int
main(int argc, char *argv[])
{
    char *tried_paths[NPATHS], *exec_errors[NPATHS];
    int i = 0, j, n = NPATHS, dashdash = 0, m;
    char **args, *p;
    char *fullprogpath;
    struct pyq_opts opts;

    fullprogpath = get_progpath(argv[0]);
    parse_opts(&opts, &argc, argv);
    pyq_trace = opts.trace;
    TRACE("pyq trace is on\n");
    if ((m = count_bits(opts.print))) {
        args = malloc((sizeof (char*)) * (2*m + 4));
        args[0] = fullprogpath;
        args[j = 1] = "pyq-print.q";
        if (opts.print_qbin) {
            args[++j] = "QBIN=";
            args[++j] = "?";
        }
        if (opts.print_qhome) {
            args[++j] = "QHOME=";
            args[++j] = "?";
        }
        if (opts.print_qarch) {
            args[++j] = "QARCH=";
            args[++j] = opts.qarch;
        }
         if (opts.print_cpus) {
            args[++j] = "CPUS=";
            args[++j] = opts.cpus;
        }
    }
    else {
        args = malloc((sizeof (char*)) * (argc + 4));
    #ifdef __APPLE__
        setenv("PYTHONEXECUTABLE", fullprogpath, 1);
    #endif
        args[0] = fullprogpath;
        args[1] = "python.q";
        for (i = j = 1; i < argc; ++i) {
            if (!dashdash && !opts.run_q && strlen(argv[i]) == 2 && argv[i][0] == '-') {
                if (argv[i][1] == '-') {
                    dashdash = 1;
                }
                else {
                    args[++j] = p = malloc(4);
                    strcpy(p, argv[i]);
                    p[2] = '@';
                    p[3] = '\0';
                }
            }
            else {
                args[++j] = argv[i];
            }
        }
    }
    if (!dashdash && !opts.run_q)
        args[++j] = "-q";
    args[++j] = NULL;
    TRACE("prog = %s\n", fullprogpath);
#ifdef __linux__
    taskset(opts.cpus);
#endif

    if (opts.qbin)
        exec_q(&opts, args);
    else {
        int attempt = 0;
        for(i = 0; ;++i) {
           attempt = find_q(args[0], &opts, attempt);
            if (attempt == -1)
                break;
            TRACE("qbin = %s\n", opts.qbin);
            if (pyq_trace) {
                printf("args =");
                char **p;
                for (p = args; *p; ++p) {
                    printf(" %s", *p);
                }
                printf("\n");
            }
            exec_q(&opts, args);
            tried_paths[i] = opts.qbin;
            exec_errors[i] = strdup(strerror(errno));
        }
    }
    /* we can only get here on error */
    /* Normally diagnostic printing is done by q, but if q could not be exec'd we still want to see it */
    if (opts.print_qhome)
        printf("QHOME=%s\n", opts.qhome);
    if (opts.print_qbin)
        printf("QBIN=%s\n", opts.qbin);
    if (opts.print_qarch)
        printf("QARCH=%s\n", opts.qarch);
    if (opts.print_cpus)
        printf("CPUS=%s\n", opts.cpus);

    if (!opts.print) {
        fprintf(stderr, "Failed to find working q executable. Tried paths:\n");
        for (n = i, i = 0; i < n; ++i) {
            fprintf(stderr, "  %s: %s\n", tried_paths[i], exec_errors[i]);
        }
        return 1;
    }
    return 0;
}

