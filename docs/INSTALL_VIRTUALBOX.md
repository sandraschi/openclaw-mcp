# OpenClaw VirtualBox Installation Guide
**Ubuntu Server 24.04 + Docker + Tailscale**

## Prerequisites
- VirtualBox 7.2.6 (✅ installed)
- 8GB RAM minimum (16GB recommended)
- 40GB free disk space
- Tailscale account

---

## Phase 1: Download Ubuntu Server (5 min)

1. **Get Ubuntu Server ISO**
   ```
   https://ubuntu.com/download/server
   ```
   - Download: **Ubuntu Server 24.04.1 LTS** (~2.6 GB)
   - Save to: `D:\ISOs\` or your preferred location

---

## Phase 2: Create VirtualBox VM (10 min)

### VM Configuration

1. **Open VirtualBox**, click **New**

2. **Basic Settings**
   - Name: `openclaw-vm`
   - Type: `Linux`
   - Version: `Ubuntu (64-bit)`
   - Click **Next**

3. **Memory**
   - RAM: `4096 MB` (minimum) or `8192 MB` (recommended)
   - Click **Next**

4. **Hard Disk**
   - Create a virtual hard disk now
   - VDI (VirtualBox Disk Image)
   - Dynamically allocated
   - Size: `40 GB`
   - Click **Create**

5. **Network Configuration** (CRITICAL for Tailscale + host access)
   - Select your VM → **Settings** → **Network**
   
   **Adapter 1 (NAT):**
   - Enable Network Adapter: ✅
   - Attached to: **NAT**
   - (This allows internet access for apt/docker/tailscale)
   
   **Adapter 2 (Host-Only):**
   - Enable Network Adapter: ✅
   - Attached to: **Host-only Adapter**
   - Name: `VirtualBox Host-Only Ethernet Adapter`
   - (This creates a private network for host → VM access)

6. **Storage**
   - Select your VM → **Settings** → **Storage**
   - Click **Empty** under Controller: IDE
   - Click the disk icon → **Choose a disk file**
   - Select the Ubuntu Server ISO you downloaded
   - Click **OK**

---

## Phase 3: Install Ubuntu Server (10 min)

1. **Start the VM**, wait for boot menu

2. **Installation Steps** (use arrow keys, Enter to select)
   - Language: **English**
   - Update to new installer: **Continue without updating**
   - Keyboard: **English (US)** (or your preference)
   - Installation type: **Ubuntu Server** (default)
   - Network: **Accept defaults** (both adapters should show)
   - Proxy: **Leave blank**, Continue
   - Mirror: **Default**, Continue
   - Storage: **Use entire disk** (default), Continue, Continue
   - Confirm destructive action: **Continue**

3. **Profile Setup**
   - Your name: `sandra` (or your preference)
   - Server name: `openclaw-vm`
   - Username: `sandra`
   - Password: *[your secure password]*
   - Continue

4. **SSH Setup**
   - Install OpenSSH server: **✅ YES** (spacebar to select)
   - Continue

5. **Featured Server Snaps**
   - **Don't select anything** (we'll install Docker manually)
   - Continue

6. **Wait for installation** (~5 minutes)

7. **When "Installation complete!" appears**
   - Select **Reboot Now**
   - Press Enter when prompted to remove installation media

8. **Login**
   - Username: `sandra`
   - Password: *[your password]*

---

## Phase 4: Initial Ubuntu Setup (5 min)

### Update system packages

```bash
sudo apt update && sudo apt upgrade -y
```

### Install essential tools

```bash
sudo apt install -y curl git vim net-tools
```

### Get VM's IP addresses

```bash
ip addr show
```

Look for:
- **enp0s3** (NAT adapter): Will have an IP like `10.0.2.15`
- **enp0s8** (Host-Only adapter): Will have an IP like `192.168.56.XXX`

**Write down the Host-Only IP** (e.g., `192.168.56.101`) - you'll need this!

---

## Phase 5: Install Docker (5 min)

### Add Docker's official GPG key and repository

```bash
# Add Docker's GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index
sudo apt update
```

### Install Docker Engine and Docker Compose

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### Add your user to docker group (avoid sudo)

```bash
sudo usermod -aG docker sandra
```

### Apply group changes (logout/login)

```bash
# Exit and log back in
exit
# [Login again with your credentials]
```

### Verify Docker installation

```bash
docker --version
docker compose version
```

---

## Phase 6: Install OpenClaw (10 min)

### Clone OpenClaw repository

```bash
cd ~
git clone https://github.com/openclaw/openclaw.git
cd openclaw
```

### Run Docker setup script

```bash
./docker-setup.sh
```

**Interactive Setup Prompts:**

1. **Onboarding method**: Choose `manual` (arrow keys, Enter)
2. **Gateway type**: Choose `Local gateway`
3. **Model provider**: Choose `OpenAI` with `ChatGPT OAuth` (cost control via token)
4. **API Configuration**: Follow prompts to connect OpenAI
5. **Tailscale**: **SKIP for now** (we'll configure separately)
6. **Other prompts**: Accept defaults

### Verify containers are running

```bash
docker compose ps
```

You should see:
- `openclaw-gateway-1` (running)
- `openclaw-cli` (may be exited - this is normal, it's a utility)

---

## Phase 7: Install and Configure Tailscale (5 min)

### Install Tailscale in the VM

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

### Start Tailscale

```bash
sudo tailscale up
```

**Follow the URL** it provides to authenticate with your Tailscale account.

### Get Tailscale IP

```bash
tailscale ip -4
```

**Write down this IP** (e.g., `100.64.X.X`) - this is your secure remote access IP!

---

## Phase 8: Access OpenClaw (2 min)

### From your Windows host machine

You now have **three ways** to access OpenClaw:

1. **Host-Only Network** (local access only)
   ```
   http://192.168.56.101:18789
   ```

2. **Tailscale** (secure remote access from anywhere)
   ```
   http://100.64.X.X:18789
   ```

3. **Within the VM** (for testing)
   ```
   http://localhost:18789
   ```

### Get dashboard access token

Inside the VM, run:

```bash
docker compose run --rm openclaw-cli dashboard --no-open
```

This will output a URL with a token:
```
http://localhost:18789?token=YOUR_TOKEN_HERE
```

**Copy that token**, then access OpenClaw from your Windows browser:
```
http://192.168.56.101:18789?token=YOUR_TOKEN_HERE
```

---

## Phase 9: Configure openclaw-mcp on Host (5 min)

On your **Windows host**, update your openclaw-mcp config:

### Set environment variables

```powershell
$env:OPENCLAW_GATEWAY_URL = "http://192.168.56.101:18789"
$env:OPENCLAW_GATEWAY_TOKEN = "YOUR_TOKEN_HERE"
```

Or add to your MCP client config:

```json
"openclaw-mcp": {
  "command": "python",
  "args": ["-m", "fastmcp", "run", "src/openclaw_mcp/server.py"],
  "env": {
    "PYTHONPATH": "D:/Dev/repos/openclaw-mcp/src",
    "PYTHONUNBUFFERED": "1",
    "OPENCLAW_GATEWAY_URL": "http://192.168.56.101:18789",
    "OPENCLAW_GATEWAY_TOKEN": "YOUR_TOKEN_HERE"
  }
}
```

---

## Security Hardening (CRITICAL)

### 1. Gateway binding (already done by default)
OpenClaw in Docker binds to `0.0.0.0:18789` inside the container, but Docker only exposes it on the VM's network interfaces, **not** the public internet.

### 2. Firewall rules (optional but recommended)

Inside the VM:

```bash
# Install UFW (firewall)
sudo apt install -y ufw

# Allow SSH (so you don't lock yourself out)
sudo ufw allow 22/tcp

# Allow OpenClaw only from host network and Tailscale
sudo ufw allow from 192.168.56.0/24 to any port 18789
sudo ufw allow from 100.64.0.0/10 to any port 18789

# Enable firewall
sudo ufw enable
```

### 3. Avoid ClawHub skills marketplace
Given the malware campaign (341+ malicious skills), **DO NOT** install skills from ClawHub until the situation is resolved.

### 4. Use clawd_security tool

From your MCP client (Cursor/Claude Desktop), run:
```
clawd_security(operation="audit")
```

---

## Troubleshooting

### Can't access from host?
```bash
# Check VM IP
ip addr show enp0s8

# Check Docker containers
docker compose ps

# Check if port 18789 is listening
sudo netstat -tlnp | grep 18789
```

### Telegram pairing (optional)

If you want Telegram integration:

1. Create bot via [@BotFather](https://t.me/BotFather)
2. Get the pairing code from Telegram
3. In the VM:
   ```bash
   docker compose run --rm openclaw-cli pairing approve telegram <CODE>
   ```

---

## Next Steps

1. ✅ Test `clawd_agent` tool from Cursor/Claude Desktop
2. ✅ Explore OpenClaw web dashboard
3. ✅ Review security settings via `clawd_security`
4. ⚠️ Avoid ClawHub skills until malware cleanup confirmed

**Remote access from coffee shop**: Use Tailscale IP (`http://100.64.X.X:18789`) - fully encrypted, no port forwarding needed!

---

## Snapshot & Backup (DO THIS!)

Once everything works, **create a VirtualBox snapshot**:

1. VirtualBox → Select `openclaw-vm`
2. Machine → Take Snapshot
3. Name: `openclaw-fresh-install`

If anything breaks, you can restore to this clean state instantly.
