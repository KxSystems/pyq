#ifdef __linux__
#define _GNU_SOURCE
#endif

#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>

#ifdef __APPLE__
#include <mach-o/dyld.h>
#include <uuid/uuid.h>
#include <sys/dirent.h>

#define QBIN "/m32/q"
static char progpath[1024];
static uint32_t nsexeclength = 1024;
#endif
#ifdef __linux__
#define QBIN "/l64/q"
#include <sched.h>

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
	sched_setaffinity(0, CPU_SETSIZE, &cpu_set);
    }
    return 0;
}
#endif

#ifndef QBIN
#error "Cannot figure out QBIN"
#endif
#define QHBIN "/q" QBIN

char *
find_q(void)
{
    char *qhome, *home, *qpath;
    int pathlen;
    qhome = getenv("QHOME");
    if (qhome == NULL) {
        home = getenv("HOME");
        if (home == NULL) {
            struct passwd *pw = getpwuid(getuid());
            home = pw->pw_dir;
        }
        pathlen = strlen(home) + strlen(QHBIN) +1;
    }
    else {
        pathlen = strlen(qhome) + strlen(QBIN) + 1;
    }
    qpath = malloc(pathlen);
    if (qhome == NULL) {
        strcat(qpath, home);
        strcat(qpath, QHBIN);
    }
    else {
        strcat(qpath, qhome);
        strcat(qpath, QBIN);
    }

    return qpath;
}

int
main(int argc, char *argv[])
{
    int rc, i;
    char **args, *p, *qpath;
    qpath = find_q();
    setenv("QBIN", qpath, 1);
    args = malloc((sizeof (char*)) * (argc + 3));
#ifdef __APPLE__
    /* TODO: Check for error and dynamically allocate progpath. */
    _NSGetExecutablePath(progpath, &nsexeclength);
    args[0] = progpath;
    setenv("PYTHONEXECUTABLE", progpath, 1);
#else
    args[0] = argv[0];
#endif
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
#ifdef __linux__
    taskset();
#endif
    rc = execvp(qpath, args);
    /* we can only get here on error */
    perror(argv[0]);

    return rc;
}
