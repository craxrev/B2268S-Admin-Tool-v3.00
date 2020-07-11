# B2268S-Admin-Tool-v3.00
Unlock the admin access for the LTE Huawei B2268s V100R001C35SP100*

## Run exploit:
1. `chmod +x b2268s.py`
2. `./b2268s.py`
3. Wait..
4. Enjoy

## New credentials
- Admin : Admin
- root : admin
You can also ssh: `ssh root@192.168.1.1`
> These new credentials are not persistant after reboot, please follow the persistance method below

## Persist new credentials
1. Login with the Admin access, after using the exploit
2. Go to maintenance > backup/restore > Backup Configuration
3. Click on Backup, give it a name like "config.rom" and save
4. `chmod +x gen_rom.py` to make the file executable if not
5. `./gen_rom.py config.rom new.rom` with "custom.row" the backup from previous step and "new.rom" the new modified backup
6. Go to maintenance > backup/restore > Restore Configuration
7. Click choose file and select "new.rom" the file generated with in step 5
8. Click upload
9. Click OK
10. Router will restart, please wait
11. Verify that new credentials are persistant after reboot

### References
> An exploit for older version https://github.com/reedleoneil/B2268S-Admin-Tool-v2.00/

> Old gist for the current exploit: https://gist.github.com/craxrev/8f1fbe7abf2c2c51f6146e7b81e868f9
