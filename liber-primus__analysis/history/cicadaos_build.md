# CicadaOS (3301.iso): what Cicada actually changed

The ISO is stock Tiny Core Linux 4.7.2 (kernel `VMLINUZ`, initrd `3301.IMG`). There is no compiled custom code:
everything Cicada added is shell script or data. File mtimes inside the initrd's cpio archive survive and date
the build (1192 files are stock, dated 2012-12-27 08:37 UTC):

| UTC time | file | change |
|---|---|---|
| 2012-12-27 09:17 | etc/init.d/tc-config | `if [ -n "$SUPERUSER" ]` commented out, so `/etc/sysconfig/superuser` is always created and the tc user never auto-logs-in |
| 2012-12-27 09:19 | etc/passwd | root's shell = `/usr/local/bin/cicada` (getty autologins root, so the shell runs at boot) |
| 2012-12-30 00:31 | usr/local/bin/prime_echo | ash script: the 464 primes 2..3301, 10 per line, tab-separated, 0.05 s apart; 2 s pause after 1033 (174th prime) and after 3301. No primes missing or extra. |
| 2013-01-02 12:02 | usr/local/bin/cicada | `clear; prime_echo; clear; cat message.txt; sleep 10; reboot` |
| 2013-01-03 00:08 | usr/local/bin/message.txt(.asc) | "@1231507051321 / The key is all around you. / Good luck. / 3301", PGP-signed |
| 2013-01-03 01:23:42 | tmp/wisdom | 3368 bytes, high-entropy |
| 2013-01-03 01:25:10 | tmp/folly | byte-identical to wisdom, written 88 s later (last file in the build) |
| 2013-01-04 04:18 | 3301.IMG | gzip timestamp of the initrd |

Nothing reads `wisdom` or `folly`; they are not used by any script. `tmp/aberr` (empty) is stock Tiny Core
(extension-load error log). The CD root also carries 560.13, 560.17, _560.00, 761.MP3 (not referenced by the OS).
