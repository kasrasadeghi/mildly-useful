#!/bin/python

CHOICE='0001'

def cmd(s):
    from subprocess import check_output
    return check_output(s).decode('utf8')

def index_split(s, i):
    return s[:i], s[i:]

def find_split(s, needle):
    return index_split(s, s.index(needle))

def boot_parser(boot_string):
    rest = boot_string
    boot = dict()

    # remove 'BootXXXX* '
    boot['bootnum'], rest = rest[:len('BootXXXX')], rest[len('BootXXXX* '):]
    assert boot['bootnum'].startswith('Boot'), boot['bootnum']
    boot['bootnum'] = boot['bootnum'][4:]
    
    # parse boot name
    boot['label'], rest = find_split(rest, '\t')

    # parse boot disk
    boot['disk'], rest = find_split(rest, '/')
    boot['disk'] = boot['disk'].lstrip()

    # chomp the '/'
    assert rest[0] == '/'
    rest[1:]

    # parse boot file
    boot['file'], rest = index_split(rest, rest.index(')') + 1)

    # parse the arg
    acc = []
    for i, c in enumerate(rest):
        if i % 2 == 0:
            acc.append(c)
    acc = "".join(acc)
    boot['arg'] = acc
    
    return boot

def set_boot(boot, create=True):
    if create:
        cmd(['efibootmgr', 
            '--bootnum', boot['bootnum'],
            '--disk',    '/dev/nvme0n1',
            '--part',    '1',
            '--create',
            '--label',   boot['label'],
            '--loader',  '/vmlinuz-linux',
            '--unicode', boot['arg'],
            '--verbose'])
    else:
        cmd(['efibootmgr', 
            '--bootnum', boot['bootnum'],
            '--disk',    '/dev/nvme0n1',
            '--part',    '1',
            '--label',   boot['label'],
            '--loader',  '/vmlinuz-linux',
            '--unicode', boot['arg'],
            '--verbose'])

def get_boot(choice):
    bootoptions = cmd(['efibootmgr', '-v'])
    for boot in bootoptions.splitlines():
        if boot.startswith('Boot' + choice):
            return boot
    return None    

def main():
    boot_before = get_boot(CHOICE)
    create = boot_before is None

    boot = dict()
    #boot['arg'] = 'root=/dev/nvme0n1p3 resume=/dev/nvme0n1p2 rw initrd=\\initramfs-linux.img'
    boot['arg'] = 'root=/dev/nvme0n1p3 resume=/dev/nvme0n1p2 rw initrd=\\intel-ucode.img initrd=\\initramfs-linux.img'
    boot['bootnum'] = '0001'
    boot['label'] = 'Arch Linux'

    for k, v in boot.items():
        print(f"'{k}': '{v}'")

    set_boot(boot, create=create)
    boot_after = get_boot(CHOICE)
    print(boot_after)


if __name__ == '__main__':
    main()
