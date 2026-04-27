# Attack Path Register

- AP-001 (hypothesis only): physical access -> wrong-device failure state -> alternate TTY exposure -> local login surface visibility -> potential host-side trust-path inspection if valid credentials or another local access method is later obtained
- AP-002 (hypothesis only): network reachability to `192.168.1.70` -> SSH/rpcbind/mDNS service analysis -> service or config weakness discovery -> possible linkage to Phoenix trust workflow if on-device evidence later confirms it
- AP-003 (hypothesis only): `dev-api.n-compass.online` ELB front -> backend Kestrel application mapping -> possible cloud-side vector -> eventual correlation to local player behavior if shared identifiers or flows are proven
