# Setting up VPN Proxy for Cloudtop

Since your Cloudtop instance cannot access the VPN, we will route traffic through your Mac.

## 🚀 Correct Order of Operations & Validation

You need **two separate terminal windows** open on your Mac.

### 🛑 STOP: Disconnect VPN first!
If you are connected to GlobalProtect or any VPN, **Disconnect it now** (or the SSH connection will fail).

### 1. Refresh Credentials (Window 1)
Run this on your Mac to refresh your Google credentials.
```bash
gcert
```
*   **Verify:** Run `gcert status`. It should say "Active".

### 2. Start the SOCKS Proxy (Window 1)
Run this on your Mac. Explicitly binds to IPv4.
```bash
ssh -D 127.0.0.1:1337 -f -C -q -N 127.0.0.1
```
*(If it asks for a password, enter your Mac password).*

### 🔍 Validation Check 1 (Window 1)
Verify the proxy works **on your Mac** before proceeding.
Run this on your Mac:
```bash
curl -v --proxy socks5h://127.0.0.1:1337 https://www.google.com
```
*   **Result:** Should print HTML/SSL handshake details.
*   **If it fails:** Your Mac cannot route through the SOCKS proxy. Check your firewall or `ssh -D` command.

### 3. Connect to Cloudtop with Tunnel (Window 2)
Run this on your Mac. Explicitly binds to IPv4.
**Keep this window open!**
```bash
ssh -R 8888:127.0.0.1:1337 crutchfielda.c.googlers.com
```
*(Wait until you are fully logged in and see the Cloudtop prompt `crutchfielda@...`)*.

### 🔍 Validation Check 2 (Cloudtop)
Verify the tunnel port is listening on Cloudtop.
Run this **on Cloudtop**:
```bash
netstat -tuln | grep 8888
```
*   **Result:** Should verify `127.0.0.1:8888` is `LISTEN`.

### 4. ✅ Connect VPN Now (Mac)
Once you have verified you are logged into Cloudtop in Window 2, **Connect your GlobalProtect VPN** on your Mac.

### 🔍 Validation Check 3 (Window 1 Mac)
Verify the SOCKS proxy still works **through the VPN**.
Run this on your Mac:
```bash
curl -v --proxy socks5h://127.0.0.1:1337 https://www.google.com
```
*   **Result:** Should print HTML/SSL handshake details.
*   **If it hangs:** The VPN is blocking the SOCKS proxy.

### 5. Test Connectivity (Window 2 Cloudtop)
Run the test script **on Cloudtop**:
```bash
./test_nordstrom_vpn.sh
```
