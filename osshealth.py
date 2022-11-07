#!/QOpenSys/pkgs/bin/python3
import sys
import os
import subprocess


def call(cmd):
    ''' Executes shell cmd. Cmd must be a list of str arguments'''
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           check=True, env=os.environ, encoding='utf8')
        return r.returncode, r.stdout, r.stderr
    except subprocess.CalledProcessError as err:
        return err.returncode, err.stdout, err.stderr


def check_contains(x, y, msgList, msg):
    ''' Checks if x contains substring y. If not, adds msg to msgList '''
    if y not in x:
        msgList.append(msg)


def check_not_contains(x, y, msgList, msg):
    ''' Checks if x contains substring y. If so, adds msg to msgList '''
    if y in x:
        msgList.append(msg)


def check_binary(name, expected, msgList, msg):
    ''' Checks that the 1st occurence of a command is in expected place '''
    if expected != get_first_binary_in_path(name):
        msgList.append(msg)


def check_exists(name, msgList, msg):
    if not os.path.exists(name):
        msgList.append(msg)


def check_not_exists(name, msgList, msg):
    if os.path.exists(name):
        msgList.append(msg)


def get_first_binary_in_path(name):
    code, out, err = call(['which', name])
    if code != 0:
        return ""  # not there
    code, out, err = call(['/QOpenSys/pkgs/bin/readlink', '-f', out.rstrip()])
    assert(code == 0)
    return out.rstrip()


def check_cmd_succeeds(cmd, msgList, msg):
    ''' Cmd needs to be list of string arguments '''
    try:
        code, _, _ = call(cmd)
        if code != 0:
            msgList.append(msg)
    except BaseException:
        msgList.append(msg)


def check_yum_pkg(pkg, msgList, msg):
    ''' Checks that pkg is installed '''
    check_cmd_succeeds(['/QOpenSys/pkgs/bin/yum', 'list', 'installed', pkg],
                       msgList, msg)


def main():
    if (1 != len(sys.argv)):
        print('usage: ' + str(sys.argv[0]))
        sys.exit(1)

    errors = []
    warnings = []

    path = os.environ['PATH'].split(':')

    # shell
    if '/QOpenSys/pkgs/bin/bash' != os.environ['SHELL']:
        warnings.append('Not using /QOpenSys/pkgs/bin/bash')

    # necessary utils
    check_exists('/QOpenSys/pkgs/bin/yum', errors,
                 'Yum binary /QOpenSys/pkgs/bin/yum not present')
    check_exists('/QOpenSys/pkgs/bin/rpm', errors,
                 'Rpm binary /QOpenSys/pkgs/bin/rpm not present')
    check_exists('/QOpenSys/pkgs/bin/bash', errors,
                 'Bash binary /QOpenSys/pkgs/bin/bash not present')
    check_exists('/QOpenSys/pkgs/bin/readlink', errors,
                 'Readlink binary /QOpenSys/pkgs/bin/readlink not present')
    check_cmd_succeeds(
        ['/QOpenSys/pkgs/bin/readlink', '-f',
         '/QOpenSys/pkgs/bin/readlink'], errors,
        'Readlink /QOpenSys/pkgs/bin/readlink binary does not work')

    if '/QOpenSys/usr/bin/tar' in get_first_binary_in_path('tar'):
        warnings.append('Using PASE tar (may want to install tar-gnu)')

    # ibmi binaries
    check_contains(
        path, '/QOpenSys/pkgs/bin', errors,
        'PATH does not contain /QOpenSys/pkgs/bin, where many OSS binaries' +
        ' are located')
    check_binary(
        'rpm', '/QOpenSys/pkgs/bin/rpm', errors,
        'Not using proper RPM binary')
    check_binary(
        'ls', '/QOpenSys/pkgs/bin/ls', errors,
        'Not using GNU coreutils (may need to install "coreutils-gnu" ' +
        'package or adjust PATH)')

    # aix binaries
    check_not_contains(
        path, '/opt/freeware/bin', errors,
        'PATH contains /opt/freeware/bin (aix binaries)')
    check_not_exists(
        '/opt/freeware/bin/rpm', warnings,
        'RPM in /opt/freeware/bin/rpm is an Aix binary')
    check_not_exists(
        '/opt/freeware/bin/yum', errors,
        'YUM in /opt/freeware/bin/yum is an Aix binary')
    check_not_exists(
        '/opt/freeware/bin/gcc', errors,
        'GCC in /opt/freeware/bin/gcc is an Aix binary')
    check_not_exists(
        '/opt/bin/gcc', errors, 'GCC in /opt/bin/gcc is an Aix binary')

    if '/opt/freeware/bin/python' in get_first_binary_in_path('python'):
        errors.append('Using Aix Python in /opt/freeware/bin')
    if '/opt/freeware/bin/python' in get_first_binary_in_path('python2'):
        errors.append('Using Aix Python 2 in /opt/freeware/bin')
    if '/opt/freeware/bin/python' in get_first_binary_in_path('python3'):
        errors.append('Using Aix Python 3 in /opt/freeware/bin')

    if '/opt/freeware/bin/rpm' in get_first_binary_in_path('rpm'):
        errors.append('Using Aix RPM from /opt/freeware/bin')
    if '/opt/freeware/bin/bash' in get_first_binary_in_path('bash'):
        errors.append('Using Aix bash from /opt/freeware/bin')
    if '/opt/freeware/bin/git' in get_first_binary_in_path('git'):
        errors.append('Using Aix GIT from /opt/freeware/bin')

    if '/QOpenSys/pkgs/bin/curl' not in get_first_binary_in_path('curl'):
        errors.append('Not using curl from /QOpenSys/pkgs/bin/curl')

    # yum pkgs
    check_cmd_succeeds(
        ['/QOpenSys/pkgs/bin/yum', 'check'], errors,
        'RPM database sanity check failed')
    check_yum_pkg(
        'ca-certificates-mozilla', warnings,
        'ca-certificates-mozilla not installed - some networking commands' +
        ' may not work')
    check_yum_pkg('bash', errors, 'bash not installed through yum')
    check_yum_pkg(
        'coreutils-gnu', errors, 'coreutils-gnu not installed through yum')

    # 5733OPS
    code, out, err = call(
        ['/QOpenSys/usr/bin/system',
            'QSYS/CHKPRDOPT PRDID(5733OPS) OPTION(*BASE)'])
    if code != 0 and 'CPF0C4A' in err:
        warnings.append('5733OPS is still installed')

    if '/QOpenSys/QIBM' in get_first_binary_in_path('python'):
        errors.append('Using 5733OPS Python')
    if '/QOpenSys/QIBM' in get_first_binary_in_path('python2'):
        errors.append('Using 5733OPS Python 2')
    if '/QOpenSys/QIBM' in get_first_binary_in_path('python3'):
        errors.append('Using 5733OPS Python 3')

    if '/QOpenSys/QIBM' in get_first_binary_in_path('node'):
        errors.append('Using 5733OPS Node')
    if '/QOpenSys/QIBM' in get_first_binary_in_path('npm'):
        errors.append('Using 5733OPS Npm')
    if '/QOpenSys/QIBM' in get_first_binary_in_path('bash'):
        errors.append('Using 5733OPS Bash')

    # display results
    if len(errors) > 0:
        print('\nErrors found:')
        for e in errors:
            print(e)
    else:
        print('\nNo errors')

    if len(warnings) > 0:
        print('\nWarnings found:')
        for e in warnings:
            print(e)
    else:
        print('\nNo warnings')


if __name__ == '__main__':
    main()
