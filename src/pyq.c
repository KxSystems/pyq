#ifdef __linux__
#  define _GNU_SOURCE
#endif

#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <pwd.h>
#include <limits.h>
#ifdef __APPLE__
#  include <mach-o/dyld.h>
#  include <uuid/uuid.h>
#  include <sys/dirent.h>
#endif /* __APPLE__ */

#define TRACE if(pyq_trace) printf
static int pyq_trace;
static char progpath[PATH_MAX];

#ifdef __APPLE__
static char*
get_progpath(const char *progname)
{
    uint32_t nsexeclength = PATH_MAX;
    /* TODO: Check for error and dynamically allocate progpath. */
    _NSGetExecutablePath(progpath, &nsexeclength);
    return strdup(progpath);
}
#elif defined(__linux__) /* __APPLE__ */
#include <sched.h>
static char *
get_progpath(const char *progname)
{
    char* path;
    char *b, *e, *r;
    int n, m;
    struct stat sb;
    if (progname[0] == '/')
        return strdup(progname);
    if (progname[0] == '.' || strchr(progname, '/')) {
        if (!getcwd(progpath, sizeof(progpath))) {
            perror("getcwd");
            exit(1);
        }
        if (!strncmp(progname, "./", 2)) {
            strcat(progpath, progname + 1);
            TRACE("Replace '.' in %s with cwd.  Got %s\n", progname, progpath);
        }
        else {
            strcat(progpath, "/");
            strcat(progpath, progname);
            TRACE("Prepend %s with cwd.  Got %s\n", progname, progpath);
        }
        return strdup(progpath);
    }
    /* search from prog in the path */
    path = getenv("PATH");
    n = strlen(progname);
    for (b = e = path; e; b = e + 1) {
        e = strchr(b, ':');
        if (e == NULL)
            e = b + strlen(b);
        m = e - b;
        r = malloc(n + m + 2);
        strncpy(r, b, m);
        r[m] = '/';
        strcpy(r + m + 1, progname);
        if (stat(r, &sb) != -1) {
            /* TODO: Check the executable bit. */
            return r;
        }
        free(r);
    }
    /* If not found - leave as is */
    return strdup(progname);
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
taskset(void)
{
    char *cpus, *test_cpus;
    cpus = getenv("CPUS");
    test_cpus = getenv("TEST_CPUS");
    if (cpus) {
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

/* QHOME priority:
    1. QHOME is already set in the environment.
    2. VIRTUAL_ENV is set -> QHOME/$VIRTUAL_ENV/q
    3. Next to pyq executable
    4. ~/q
*/
char *
find_q(const char* progpath)
{
    char *qhome = NULL, *prefix = NULL, *qpath = NULL, *p;
    static int attempt = 0;
    switch (++attempt) {
        case 1:
            if ((qhome = getenv("QHOME"))) {
                qhome = strdup(qhome);
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
            return NULL;
    }
    TRACE("qhome = %s\n", qhome);
    qpath = malloc(strlen(qhome) + strlen(xstr(QARCH)) + 4);
    strcpy(qpath, qhome);
    strcat(qpath, "/" xstr(QARCH) "/q");
    setenv("QBIN", qpath, 1);

    return qpath;
}

#define NPATHS 4

int
main(int argc, char *argv[])
{
    char *tried_paths[NPATHS];
    int rc = 0, i, n;
    char **args, *p, *qpath;
    char *fullprogpath;
    pyq_trace = argc > 1 && !strcmp("--pyq-trace", argv[1]);
    if (pyq_trace) {
        /* remove option from argv */
        --argc;
        for (i = 1; i < argc; ++i) {
            argv[i] = argv[i+1];
        }
        argv[argc] = NULL;
        printf("pyq trace is on\n");
    }
    args = malloc((sizeof (char*)) * (argc + 3));
    fullprogpath = get_progpath(argv[0]);
#ifdef __APPLE__

    args[0] = progpath;
    setenv("PYTHONEXECUTABLE", progpath, 1);
#endif
    args[0] = fullprogpath;
    args[1] = "python.q";
    args[argc + 1] = "-q";
    args[argc + 2] = NULL;
    for (i = 1; i < argc; ++i) {
        if (argv[i][0] == '-' && strlen(argv[i] + 1) == 1) {
            args[i+1] = p = malloc(4);
            strcpy(p, argv[i]);
            p[2] = '@';
            p[3] = '\0';
        }
        else {
            args[i+1] = argv[i];
        }
    }
    TRACE("prog = %s\n", fullprogpath);
#ifdef __linux__
    taskset();
#endif

    for(i = 0; ;++i) {
        qpath = find_q(args[0]);
        if (qpath) {
            TRACE("qbin = %s\n", qpath);
            if (pyq_trace) {
                printf("args =");
                char **p;
                for (p = args; *p; ++p) {
                    printf(" %s", *p);
                }
                printf("\n");

            }
            /* Flush streams before exec. */
            fflush(stdout);
            fflush(stderr);
            rc = execvp(qpath, args);
            tried_paths[i] = qpath;
        }
        else {
            break;
        }
    }
    /* we can only get here on error */
    if (!pyq_trace) /* In verbose mode, paths are already printed */
        for (n = i, i = 0; i < n; ++i) {
            fprintf(stderr, "qbinpath = %s\n", tried_paths[i]);
        }
    perror(qpath);
    return rc;
}
