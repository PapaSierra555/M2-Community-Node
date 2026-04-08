# Mission 2 - Monero (XMR) Community Node Infrastructure

> **Platform:** Raspberry Pi 5 (16 GB RAM) | 1 TB SSD | 10" Mini-Rack
> **Role:** Privacy-preserving cryptocurrency node for portable community deployment

---

## What This Is (New Users)

The M2 Community Node runs a **Monero (XMR) pruned node** — a self-hosted, privacy-preserving cryptocurrency node that your community can use directly, without relying on a third-party server.

**Why it matters:** When you use Monero through a wallet, that wallet has to connect to *some* node to query the blockchain. If you connect to a random public node, that node sees your IP, your transaction history queries, and your balance checks. Running your own node means only you see that data.

**What you can do with it:**

- **Send and receive XMR privately** — connect your wallet (Feather, Monero GUI, etc.) to `YOUR_NODE_IP:18089` via Tailscale VPN instead of a public remote node
- **Use it as a community service** — give community members access via Headscale VPN so they can use the node without running their own
- **Verify your own transactions** — full independent validation, no trust required
- **Run a Tor hidden service** — expose the RPC as a `.onion` address for anonymous access

**What it is not:** This is not an exchange. You cannot buy or sell XMR through this node. It is a private backend that wallets talk to — the node broadcasts transactions and syncs the blockchain, but the keys and funds stay in the user's wallet.

**To use it:** Install [Feather Wallet](https://featherwallet.org) → Settings → Node → enter your node's Tailscale IP and port 18089. That's it.

---

## Table of Contents

1. [Monero Full Node (monerod) on Raspberry Pi 5](#1-monero-full-node-monerod-on-raspberry-pi-5)
2. [Monero Remote Node (Alternative)](#2-monero-remote-node-alternative)
3. [Privacy Architecture](#3-privacy-architecture)
4. [Monero Wallet Infrastructure](#4-monero-wallet-infrastructure)
5. [Storage Planning](#5-storage-planning)
6. [Docker Deployment](#6-docker-deployment)
7. [Feasibility Assessment](#7-feasibility-assessment)
8. [Resource Allocation Impact](#8-resource-allocation-impact)

---

## 1. Monero Full Node (monerod) on Raspberry Pi 5

### 1.1 Resource Requirements on ARM64 (Pi 5)

| Metric | Full Node | Pruned Node |
|---|---|---|
| **Blockchain size (2025-2026)** | ~220-230 GB | ~90-95 GB |
| **RAM during initial sync** | 4-6 GB active (peaks higher with DB cache) | 3-4 GB active |
| **RAM steady-state** | 1-2 GB | ~1 GB |
| **CPU during sync** | All 4 cores saturated (Cortex-A76 @ 2.4 GHz) | Same |
| **CPU steady-state** | 5-15% single core for block validation | Same |
| **Sync time (from scratch)** | 2-4 weeks on Pi 5 with SSD | 2-3 weeks |
| **Network (sync)** | 50-100 GB download | ~35-50 GB download |
| **Network (steady-state)** | 20-50 GB/month (depends on peer count) | 15-30 GB/month |

**Key observations:**

- The Pi 5's quad Cortex-A76 cores are a major improvement over Pi 4 for Monero sync. The A76 is roughly 2x faster per-core than the A72 in the Pi 4.
- Initial blockchain sync is **CPU-bound** on ARM due to cryptographic verification of every transaction (RingCT, Bulletproofs+). This is the primary bottleneck.
- Steady-state operation (receiving/relaying new blocks every ~2 minutes) is very lightweight.
- SSD random I/O performance is critical -- the LMDB database requires heavy random reads during sync.

### 1.2 ARM64 Binaries

- **Pre-built binaries**: The Monero project provides official `linux-armv8` (ARM64/aarch64) binaries on every release. No compilation needed.
- **Compilation from source**: Fully supported on ARM64. Build time on Pi 5 is approximately 30-60 minutes. Requires ~4 GB RAM during compilation.
- **Docker images**: `ghcr.io/sethforprivacy/simple-monerod` provides multi-arch images including `linux/arm64`.

### 1.3 GUI Wallet vs CLI Wallet

| Aspect | GUI Wallet | CLI Wallet |
|---|---|---|
| **Ease of use** | Point-and-click, suitable for beginners | Command-line only, steeper learning curve |
| **Resource overhead** | Heavier (Qt/QML framework) | Minimal |
| **Headless operation** | Not practical on a server Pi | Ideal for headless Pi |
| **Remote access** | Requires VNC/display forwarding | SSH-friendly |
| **Recommendation** | Not recommended for community node | **Preferred** -- use CLI + Wallet RPC |

**For a community node**: Run `monerod` (daemon) and optionally `monero-wallet-rpc` for programmatic access. Community members connect with their own wallets (Feather, Cake Wallet, Monerujo) pointed at the node's restricted RPC.

### 1.4 Pruned Node vs Full Node

| Feature | Full Node | Pruned Node |
|---|---|---|
| **Storage** | ~230 GB (growing ~20-24 GB/year) | ~95 GB (growing ~8-10 GB/year) |
| **Validation** | Full -- verifies entire chain | Full -- verifies entire chain |
| **Serving blocks to peers** | All blocks available | Only 1/8 of historical ring data retained |
| **Transaction relay** | Full capability | Full capability |
| **Wallet scanning** | Full historical scan | Full historical scan |
| **Privacy** | No difference | No difference |
| **Network contribution** | Helps bootstrap new nodes faster | Slightly reduced bootstrap capability |

**Recommendation for Pi 5 with 1 TB SSD**: Run a **pruned node**. At ~95 GB, this leaves ample room for other Mission 2 services on the shared 1 TB SSD. Pruning removes 7/8 of unnecessary ring signature data while maintaining full validation and privacy. There are no security or privacy downsides.

---

## 2. Monero Remote Node (Alternative)

### 2.1 Running monerod as a Public Remote Node

A public remote node allows community members to connect their wallets without running their own node. This is the primary use case for a community node.

```bash
monerod \
  --restricted-rpc \
  --rpc-bind-ip=0.0.0.0 \
  --rpc-restricted-bind-port=18089 \
  --confirm-external-bind \
  --public-node \
  --prune-blockchain
```

**Key flags:**
- `--restricted-rpc`: Limits RPC to safe read-only methods (prevents abuse)
- `--rpc-restricted-bind-port=18089`: Standard restricted RPC port
- `--public-node`: Advertises the node on the Monero P2P network so wallets can discover it
- `--confirm-external-bind`: Required when binding to 0.0.0.0

### 2.2 RPC Configuration for Wallet Connections

Wallets connect to the node via the restricted RPC endpoint:

```
Host: <node-ip-or-onion>
Port: 18089
```

Compatible wallets: Feather Wallet, Cake Wallet, Monerujo, Monero CLI/GUI, MyMonero.

### 2.3 Security Hardening

**Authentication (optional for restricted RPC):**
```bash
--rpc-login=user:password
```

**Rate limiting:**
- monerod does not have built-in rate limiting on RPC
- Use a reverse proxy (Nginx/Caddy) in front of RPC for rate limiting:

```nginx
# Nginx rate limiting — bind monerod to 127.0.0.1:18090, expose via Nginx on 18089
limit_req_zone $binary_remote_addr zone=monero_rpc:10m rate=30r/m;

server {
    listen 18089;
    location / {
        limit_req zone=monero_rpc burst=10;
        proxy_pass http://127.0.0.1:18090;  # monerod restricted RPC on internal port
    }
}
```
> When using this pattern, start monerod with `--rpc-restricted-bind-ip=127.0.0.1 --rpc-restricted-bind-port=18090` so it does not bind directly on 18089.

**Tor-only RPC:**
- Expose the restricted RPC port only as a Tor hidden service
- Do not bind to 0.0.0.0 on clearnet -- bind to 127.0.0.1 only
- Configure Tor hidden service to forward to localhost:18089

### 2.4 Resource Comparison

| Configuration | Storage | RAM (Steady) | Bandwidth | Community Value |
|---|---|---|---|---|
| Full node (not public) | ~230 GB | 1-2 GB | 20-50 GB/mo | Supports network only |
| Pruned node (not public) | ~95 GB | ~1 GB | 15-30 GB/mo | Supports network only |
| **Pruned public remote node** | **~95 GB** | **~1-2 GB** | **30-60 GB/mo** | **Community wallets connect here** |
| Full public remote node | ~230 GB | 1-2 GB | 40-80 GB/mo | Maximum community service |

---

## 3. Privacy Architecture

### 3.1 Tor Integration

Monero has native Tor support via the `--tx-proxy` and `--anonymous-inbound` flags.

> **Important limitation confirmed in real-world testing:** Full blockchain sync (initial block download) **cannot run over Tor hidden services (.onion)**. Only handshakes, peer timed syncs, and transaction broadcasts are supported over .onion. Additionally, Tor exit nodes commonly block port 18080, making `--proxy 127.0.0.1:9050` unreliable for the pre-sync phase. **Do not attempt to use Tor for the Windows pre-sync.** Tor is appropriate for the Pi's steady-state operation (transaction relay and .onion RPC exposure) but not for initial blockchain download.

**Transaction relay over Tor (outbound):**
```bash
monerod \
  --tx-proxy tor,127.0.0.1:9050,16 \
  --no-igd
```

This routes outbound transaction relay to `.onion` peers through the local Tor SOCKS proxy at port 9050, with up to 16 outbound Tor connections.

**Receiving connections over Tor (inbound):**
```bash
monerod \
  --anonymous-inbound <your-onion-address>:18083,127.0.0.1:18083,64 \
  --tx-proxy tor,127.0.0.1:9050,16
```

This advertises your `.onion` address to Tor-capable peers so they can connect to you.

**Tor-only mode (hiding from clearnet entirely):**
```bash
monerod \
  --tx-proxy tor,127.0.0.1:9050,16 \
  --anonymous-inbound <your-onion>.onion:18083,127.0.0.1:18083,64 \
  --add-exclusive-node <seed-onion-1>.onion:18083 \
  --add-exclusive-node <seed-onion-2>.onion:18083 \
  --no-igd \
  --hide-my-port
```

Using `--add-exclusive-node` with only `.onion` addresses ensures no clearnet connections are made.

### 3.2 I2P Integration

Monero also supports I2P via the same mechanism:

```bash
monerod \
  --tx-proxy i2p,127.0.0.1:4447 \
  --anonymous-inbound <your-i2p-address>.b32.i2p:18083,127.0.0.1:18083,64
```

I2P SOCKS proxy typically listens on port 4447 (via i2pd).

### 3.3 Dual Anonymity Network Configuration

For maximum privacy, run both Tor and I2P simultaneously:

```bash
monerod \
  --tx-proxy tor,127.0.0.1:9050,16 \
  --tx-proxy i2p,127.0.0.1:4447,16 \
  --anonymous-inbound <onion>:18083,127.0.0.1:18083,64 \
  --anonymous-inbound <i2p>.b32.i2p:18083,127.0.0.1:18083,64 \
  --no-igd
```

### 3.4 P2P Over Tor: Pros and Cons

| Aspect | Clearnet P2P | Tor P2P |
|---|---|---|
| **IP privacy** | Node IP visible to peers | Node IP hidden |
| **Sync speed** | Normal (days to weeks) | 3-10x slower due to Tor latency |
| **Connection reliability** | High | Moderate (onion circuits drop) |
| **Peer diversity** | Large peer pool | Smaller Tor-only peer pool |
| **Recommended approach** | Initial sync on clearnet, then switch | Steady-state operation |

**Practical recommendation**: Perform the initial blockchain sync over clearnet (2-4 weeks on Pi 5), then switch to Tor-only operation for privacy. Syncing from scratch over Tor on a Pi 5 could take 1-3 months and is not practical.

### 3.5 Important Privacy Caveat

From the Monero documentation: "The usage of Tor/I2P is still considered experimental -- there are a few pessimistic cases where privacy is leaked." Specifically:
- If the node makes any clearnet connections, IP correlation is possible
- Transaction timing analysis is still a research concern
- The initial sync necessarily reveals interest in Monero to the ISP (unless over VPN/Tor)

---

## 4. Monero Wallet Infrastructure

### 4.1 Monero Wallet RPC

The `monero-wallet-rpc` service provides a JSON-RPC interface for programmatic wallet access:

```bash
monero-wallet-rpc \
  --rpc-bind-port 18082 \
  --rpc-bind-ip 127.0.0.1 \
  --daemon-address 127.0.0.1:18081 \
  --wallet-dir /path/to/wallets \
  --rpc-login user:password \
  --disable-rpc-login  # OR use rpc-login for auth
```

**Capabilities:**
- Create/open/close wallets
- Generate receiving addresses (subaddresses)
- Check balances, transfer history
- Send transactions programmatically
- Multisig operations

**Use case for community node**: Allow automated services or scripts to interact with Monero wallets. Bind only to localhost -- never expose wallet RPC to the network.

### 4.2 Recommended Wallets for Community Members

| Wallet | Platform | Open Source | Key Features |
|---|---|---|---|
| **Feather Wallet** | Desktop (Linux, Windows, macOS) | Yes | Tor built-in, lightweight, advanced features |
| **Cake Wallet** | iOS, Android | Yes | User-friendly, built-in exchange, Tor support |
| **Monerujo** | Android | Yes | Lightweight, supports remote nodes, Tor via Orbot |
| **Monero CLI** | All platforms | Yes (official) | Most feature-complete, multisig support |
| **Monero GUI** | Desktop | Yes (official) | Full node integration, hardware wallet support |

**Recommendation**: Feather Wallet for desktop users, Cake Wallet for iOS, Monerujo for Android. All support connecting to a remote node (the community Pi node).

### 4.3 Community Wallet Setup

For a community-managed node:
1. **Each member creates their own wallet** on their device
2. **Point wallets at the community node's restricted RPC** (port 18089)
3. The node validates transactions and provides blockchain data
4. **Private keys never touch the node** -- wallets do all key management locally

This is the safest architecture: the node is a shared infrastructure service, not a custodial wallet.

### 4.4 Multisig Wallet for Community Treasury

Monero supports M-of-N multisig natively via the CLI wallet and the Multisig Messaging System (MMS).

**Common configurations:**
- **2-of-3**: Three keyholders, any two can authorize spending. Good for small groups.
- **3-of-5**: Five keyholders, three required. Better for larger communities.
- **5-of-7**: High security for significant treasuries.

**Setup process (CLI):**
1. Each participant creates a wallet
2. Exchange `multisig_info` between all participants (via MMS or manually)
3. Finalize the multisig wallet
4. Generate a shared receiving address
5. Spending requires M participants to sign the transaction in rounds

**Limitations:**
- Multisig is **CLI-only** (no GUI support for setup)
- Requires careful key exchange and coordination
- The MMS simplifies the process but still requires technical comfort
- Latency between signing rounds can be inconvenient for geographically distributed groups

**Security note**: Monero multisig was audited and bugs were fixed in PR #8149 (mid-2022). Current versions are considered safe for use.

---

## 5. Storage Planning

### 5.1 Current Blockchain Size and Growth

| Metric | Value |
|---|---|
| **Full blockchain (Feb 2026)** | ~230 GB |
| **Pruned blockchain (Feb 2026)** | ~95 GB |
| **Annual growth rate (full)** | ~20-24 GB/year |
| **Annual growth rate (pruned)** | ~8-10 GB/year |
| **Average block size** | ~55-75 KB |
| **Block interval** | ~2 minutes |

### 5.2 Storage Projections (Pruned Node)

| Year | Estimated Pruned Size |
|---|---|
| 2026 | ~95 GB |
| 2027 | ~105 GB |
| 2028 | ~115 GB |
| 2030 | ~135 GB |
| 2035 | ~185 GB |

A pruned node comfortably fits within a 250 GB allocation for the foreseeable future.

### 5.3 SSD vs HDD

| Factor | SSD | HDD |
|---|---|---|
| **Random I/O** | Excellent -- critical for LMDB | Very poor |
| **Sync speed** | 2-4 weeks on Pi 5 | 2-6 months (unusable) |
| **Steady-state** | Near-instant block verification | Noticeable delays |
| **Verdict** | **Required** | Not recommended |

Monero's LMDB database is extremely random-I/O heavy. **An SSD is effectively mandatory**, not optional.

### 5.4 External USB 3.0 SSD vs Internal

The Pi 5 does not have internal SATA/NVMe by default. Options:
- **USB 3.0 SSD**: Fully adequate. USB 3.0 provides up to 5 Gbps, far exceeding monerod's I/O needs. Random IOPS may be slightly lower than direct NVMe but still vastly better than HDD.
- **NVMe via HAT**: Pi 5 supports M.2 NVMe via the official HAT. Offers better random I/O but adds cost and complexity.
- **Recommendation**: USB 3.0 SSD is sufficient and simpler for a portable rack build.

### 5.5 1 TB SSD Allocation

Recommended partition/allocation for the shared 1 TB SSD:

| Service | Allocation | Notes |
|---|---|---|
| **OS + Docker** | 30 GB | Raspberry Pi OS + container images |
| **Monero (pruned)** | 150 GB | ~95 GB current + growth headroom |
| **Matrix/Synapse** | 50-100 GB | Chat history, media |
| **ATAK Server** | 20 GB | Map data, CoTs |
| **Reticulum** | 5 GB | Minimal storage |
| **Tor/I2P** | 5 GB | Relay cache |
| **Logs + misc** | 10 GB | System logs, monitoring |
| **Free space** | ~680-730 GB | Buffer for growth |

**Monero's 150 GB allocation** provides ~5 years of pruned node growth without intervention.

---

## 6. Docker Deployment

### 6.1 Recommended Docker Image

**`ghcr.io/sethforprivacy/simple-monerod`** (by Seth For Privacy)
- Built from source, verified against upstream Monero releases
- Multi-architecture: `linux/amd64` and `linux/arm64`
- Minimal attack surface
- Actively maintained
- [GitHub Repository](https://github.com/sethforprivacy/simple-monerod-docker)

### 6.2 Docker Compose Configuration

```yaml
# =============================================================================
# Monero Community Node - Docker Compose
# Platform: Raspberry Pi 5 (ARM64) | 1 TB SSD
# =============================================================================

services:
  # ---------------------------------------------------------------------------
  # Monero Daemon (monerod) - Pruned Public Node
  # ---------------------------------------------------------------------------
  monerod:
    image: ghcr.io/sethforprivacy/simple-monerod:latest
    container_name: monerod
    restart: unless-stopped
    user: "${FIXUID:-1000}:${FIXGID:-1000}"
    volumes:
      - monero-data:/home/monero/.bitmonero
    ports:
      # P2P port - required for network participation
      - "18080:18080"
      # Restricted RPC - for community wallet connections
      - "18089:18089"
    command:
      # --- Network ---
      - --rpc-restricted-bind-ip=0.0.0.0
      - --rpc-restricted-bind-port=18089
      - --confirm-external-bind
      - --public-node
      - --no-igd
      # --- Storage ---
      - --prune-blockchain
      - --db-sync-mode=safe:sync
      # --- Security ---
      - --enable-dns-blocklist
      - --out-peers=32
      - --in-peers=64
      - --limit-rate-up=1048576    # 1 MB/s upload limit
      - --limit-rate-down=1048576  # 1 MB/s download limit
      # --- Logging ---
      - --log-level=0
      - --max-log-file-size=10485760  # 10 MB
      - --max-log-files=3
    # Resource limits for Pi 5 coexistence
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"
        reservations:
          memory: 1G
          cpus: "0.5"
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://127.0.0.1:18081/get_info || exit 1"]
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 300s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  # ---------------------------------------------------------------------------
  # Tor Proxy - For anonymous transaction relay (optional)
  # ---------------------------------------------------------------------------
  tor:
    image: osminogin/tor-simple:latest
    container_name: monero-tor
    restart: unless-stopped
    volumes:
      - tor-data:/var/lib/tor
      - ./torrc:/etc/tor/torrc:ro
    ports:
      - "127.0.0.1:9050:9050"   # SOCKS proxy
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: "0.5"

  # ---------------------------------------------------------------------------
  # Monero Wallet RPC (optional - for programmatic access)
  # ---------------------------------------------------------------------------
  monero-wallet-rpc:
    image: ghcr.io/sethforprivacy/simple-monerod:latest
    container_name: monero-wallet-rpc
    restart: unless-stopped
    user: "${FIXUID:-1000}:${FIXGID:-1000}"
    entrypoint: monero-wallet-rpc
    volumes:
      - wallet-data:/home/monero/wallets
    ports:
      - "127.0.0.1:18082:18082"  # Localhost only!
    command:
      - --rpc-bind-port=18082
      - --rpc-bind-ip=0.0.0.0
      - --confirm-external-bind
      - --daemon-address=monerod:18081
      - --wallet-dir=/home/monero/wallets
      - --rpc-login=${WALLET_RPC_USER:-monero}:${WALLET_RPC_PASS:-changeme}
    depends_on:
      monerod:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
    profiles:
      - wallet  # Only starts with: docker compose --profile wallet up

volumes:
  monero-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/ssd/monero/data
  tor-data:
    driver: local
  wallet-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/ssd/monero/wallets
```

### 6.3 Tor Configuration File (torrc)

Create `torrc` alongside the compose file:

```
SOCKSPort 0.0.0.0:9050
SOCKSPolicy accept 172.16.0.0/12   # Docker networks
SOCKSPolicy reject *

# Hidden service for Monero RPC (Tor-only wallet access)
HiddenServiceDir /var/lib/tor/monero-rpc/
HiddenServicePort 18089 monerod:18089

# Hidden service for Monero P2P
HiddenServiceDir /var/lib/tor/monero-p2p/
HiddenServicePort 18083 monerod:18080
```

### 6.4 Environment File (.env)

```bash
# User/Group IDs (match host user)
FIXUID=1000
FIXGID=1000

# Wallet RPC credentials (change these!)
WALLET_RPC_USER=monero
WALLET_RPC_PASS=<generate-strong-password>
```

### 6.5 Deployment Commands

```bash
# Create data directories
sudo mkdir -p /mnt/ssd/monero/{data,wallets}
sudo chown 1000:1000 /mnt/ssd/monero/{data,wallets}

# Start monerod and Tor
docker compose up -d monerod tor

# Check sync status
docker exec monerod monerod status

# View logs
docker compose logs -f monerod

# Start wallet RPC (when needed)
docker compose --profile wallet up -d

# Get Tor hidden service addresses
docker exec monero-tor cat /var/lib/tor/monero-rpc/hostname
docker exec monero-tor cat /var/lib/tor/monero-p2p/hostname
```

### 6.6 Speeding Up Initial Sync

**Option A: Import from another device**
```bash
# On a synced machine, export the blockchain
monero-blockchain-export --output-file /tmp/blockchain.raw

# Copy to Pi
scp /tmp/blockchain.raw pi@<pi-ip>:/mnt/ssd/monero/

# Import on Pi
docker exec -it monerod monero-blockchain-import \
  --input-file /home/monero/.bitmonero/blockchain.raw \
  --batch-size 5000
```

**Option B: Copy LMDB directly**
```bash
# Stop monerod on both machines
# Copy data.mdb and lock.mdb from synced machine to Pi
rsync -avP synced-machine:/path/to/bitmonero/lmdb/ /mnt/ssd/monero/data/lmdb/
```

This bypasses verification and takes only as long as the file transfer (hours, not weeks).

---

## 7. Feasibility Assessment

### 7.1 Is Raspberry Pi 5 (16 GB) Adequate for a Monero Full Node?

**YES -- the Pi 5 16 GB is adequate for a Monero pruned node.**

| Criterion | Requirement | Pi 5 Capability | Verdict |
|---|---|---|---|
| **CPU** | Multi-core ARM64 | 4x Cortex-A76 @ 2.4 GHz | Sufficient |
| **RAM** | 4 GB minimum, 8 GB recommended | 16 GB | Exceeds requirements |
| **Storage** | 95 GB pruned (SSD required) | 1 TB SSD (shared) | Ample |
| **Network** | Stable broadband | Depends on deployment site | Variable |

### 7.2 Sync Time Estimates

| Method | Estimated Time |
|---|---|
| **From scratch (clearnet, SSD)** | 2-4 weeks |
| **From scratch (Tor-only)** | 1-3 months (not recommended) |
| **Blockchain import (from another machine)** | 2-8 hours (file copy) + 0-2 days (verification) |
| **LMDB copy (trusted source)** | 1-4 hours (file transfer only) |

**Strong recommendation**: Pre-sync on a faster x86 machine and copy the LMDB database to the Pi. This reduces setup time from weeks to hours.

### 7.3 Steady-State Performance After Sync

Once synced, the Pi 5 handles Monero effortlessly:
- New blocks arrive every ~2 minutes
- Block verification takes <1 second on Pi 5
- RAM usage stabilizes at 1-2 GB
- CPU usage drops to 5-15% on one core
- Disk I/O is minimal (write one block every 2 minutes)

**The Pi 5 is overspecced for steady-state Monero operation.** The challenge is only the initial sync.

### 7.4 Alternative Hardware (If Needed)

If the Pi 5 proves too slow for initial sync or concurrent workloads:

| Hardware | CPU | RAM | Sync Time | Price (approx) |
|---|---|---|---|---|
| **Raspberry Pi 5** | 4x A76 @ 2.4 GHz | 16 GB | 2-4 weeks | $80 |
| **Intel N100 mini PC** | 4x E-core @ 3.4 GHz | 16 GB | 3-7 days | $120-180 |
| **Intel N305 mini PC** | 8x E-core @ 3.8 GHz | 16-32 GB | 2-4 days | $200-300 |

The Intel N100 is significantly faster for initial sync due to higher single-thread performance and AVX2 support (accelerates cryptographic operations). However, the Pi 5 is adequate once synced, more power-efficient (~15W vs ~25-35W), and fits the portable rack form factor better.

### 7.5 Honest Summary

- **Pi 5 is a viable Monero node** -- this is well-established in the community
- The main pain point is **initial sync time** (weeks), which is a one-time cost
- Pre-syncing on a faster machine and copying the database is the practical answer
- **16 GB RAM is overkill for Monero alone** but valuable when running alongside Matrix, ATAK, etc.
- For a portable community node, the Pi 5 is the right choice: low power, small form factor, adequate performance

---

## 8. Resource Allocation Impact

### 8.1 Monero Resource Consumption

**During initial sync (worst case):**

| Resource | Usage | Impact |
|---|---|---|
| CPU | 2-4 cores at 80-100% | Severe impact on other services |
| RAM | 3-5 GB (with DB cache) | Moderate -- 11-13 GB remaining |
| Disk I/O | Heavy random reads/writes | May bottleneck shared SSD |
| Network | 10-50 Mbps sustained | Moderate bandwidth consumption |

**Steady-state (after sync):**

| Resource | Usage | Impact |
|---|---|---|
| CPU | 5-15% one core | Negligible |
| RAM | 1-2 GB | Minimal -- 14-15 GB remaining |
| Disk I/O | Light (one block / 2 min) | Negligible |
| Network | 0.5-2 Mbps average | Minimal |

### 8.2 Impact on Other Services

| Service | During Monero Sync | After Monero Sync |
|---|---|---|
| **Matrix/Synapse** | May experience slowdowns (CPU contention) | No impact |
| **ATAK Server** | CoT relay unaffected (lightweight) | No impact |
| **Reticulum** | Unaffected (very lightweight) | No impact |
| **Tor/I2P** | Slight bandwidth contention | No impact |

### 8.3 Mitigation Strategies

1. **CPU limiting**: The Docker Compose above limits monerod to 2 cores, leaving 2 cores for other services
2. **Memory limiting**: Capped at 4 GB in Docker, preventing runaway memory growth
3. **I/O scheduling**: Linux `ionice` can deprioritize monerod's disk I/O:
   ```bash
   docker update --device-write-bps /dev/sda:50mb monerod
   ```
4. **Sync scheduling**: Start the initial sync before deploying other services, or pre-sync off-device

### 8.4 Is a Dedicated Device Warranted?

**No -- a dedicated device is not necessary.**

After the initial sync (one-time event), Monero consumes minimal resources:
- ~1-2 GB RAM out of 16 GB available
- <15% of one CPU core
- Negligible disk I/O
- Moderate but manageable network bandwidth

The Pi 5 with 16 GB has ample capacity to run monerod alongside Matrix, ATAK, Reticulum, and Tor/I2P services simultaneously. The Docker resource limits in the compose configuration above ensure Monero cannot starve other services.

---

## Appendix B: Windows Pre-Sync Field Notes

Real-world findings from executing the Phase 0 pre-sync on AT&T Fiber 1000 (Central Florida) using Windows 11 with ProtonVPN.

### What Worked

| Setting | Value |
|---|---|
| OS | Windows 11 |
| ISP | AT&T Fiber 1000 |
| VPN | ProtonVPN regular server (NOT P2P server) |
| monerod version | v0.18.4.5 "Fluorine Fermi" |
| Launch method | `.\__fix_and_launch.ps1` |
| monerod flags | `--prune-blockchain --data-dir "G:\MoneroNode\data" --log-level 1` |
| Peers at steady state | 8 outbound |
| Network height confirmed | 3,619,353 |
| Status | SYNCING confirmed |

### Failure Log

| What Was Tried | Result | Root Cause |
|---|---|---|
| No VPN on AT&T Fiber | All handshakes timeout | AT&T DPI fingerprints and drops Monero Levin P2P protocol |
| ProtonVPN P2P server | All handshakes timeout | P2P servers apply additional filtering or have blacklisted exit IPs |
| `--add-peer hostname:port` | Crashes with "Failed to initialize p2p server" | DNS resolution during p2p init fails through VPN |
| `--add-peer ip:port` | Handshake timeouts | Nodes reject connections from VPN exit IPs |
| Tor proxy `--proxy 127.0.0.1:9150` | Handshake timeouts | Tor exit nodes block port 18080 |
| Full blockchain sync over Tor .onion | Not possible | Protocol limitation — .onion only supports handshakes and tx broadcast |
| Extra flags (`--db-sync-mode`, `--out-peers 64`) | Handshake timeouts | Interfere with peer discovery under VPN/DPI conditions |
| `monerod.exe` run directly (no fix script) | "Failed to initialize p2p server" | `p2pstate.bin` corrupts to 0 bytes on every stop |

### Key Discoveries

**`p2pstate.bin` corruption:** Every time monerod stops, `p2pstate.bin` becomes zero bytes. On next start, monerod's p2p server fails to initialize. This is a Windows-specific behavior. Fix: always delete `p2pstate.bin` before launch. The `__fix_and_launch.ps1` script handles this automatically.

**AT&T DPI confirmed:** AT&T Fiber uses protocol-level Deep Packet Inspection that specifically targets the Monero Levin binary protocol signature on port 18080. TCP connection succeeds (port is open), but application-layer data is dropped. Affects all clients, all peers, consistently. VPN required.

**Tor is not a workaround for ISP DPI during sync:** Tor exit nodes have port restriction policies — most block non-standard ports including 18080. Even when an exit node allows port 18080, the Tor circuit adds latency that exceeds monerod's 5-second handshake timeout. Full blockchain sync over Tor .onion connections is not supported by the monerod protocol.

**Minimal flags are required with VPN:** Extra flags that tune peer counts or db-sync behavior interact poorly with how monerod discovers peers through VPN exit nodes. The three-flag minimal set (`--prune-blockchain`, `--data-dir`, `--log-level`) is confirmed working.

**Monero RPC (HTTP) works even when P2P doesn't:** Port 18089 HTTP RPC was reachable and returned full blockchain data even while all P2P handshakes were failing. This is a reliable diagnostic: if RPC works but P2P fails, it confirms protocol-level filtering (DPI) rather than a general connectivity problem.

### Diagnostic Commands

```powershell
# Test if P2P port is TCP-reachable (should succeed even with DPI)
Test-NetConnection -ComputerName 107.178.98.234 -Port 18080

# Test if bidirectional Monero data flow works (HTTP RPC)
Invoke-RestMethod -Uri "http://23.137.57.100:18089/get_info" -TimeoutSec 10

# Resolve seed node IPs via Google DNS (bypasses VPN DNS failures)
Resolve-DnsName node.supportxmr.com -Server 8.8.8.8

# Verify Tor SOCKS proxy is running (Tor Browser = 9150, Tor daemon = 9050)
Test-NetConnection -ComputerName 127.0.0.1 -Port 9150
```

---

## Appendix A: Quick Reference

### Ports

| Port | Protocol | Purpose |
|---|---|---|
| 18080 | TCP | P2P (peer-to-peer network) |
| 18081 | TCP | Full RPC (localhost only) |
| 18082 | TCP | Wallet RPC (localhost only) |
| 18083 | TCP | P2P over Tor/I2P |
| 18089 | TCP | Restricted RPC (public, read-only) |

### Key Directories

| Path | Contents |
|---|---|
| `/mnt/ssd/monero/data` | Blockchain database (LMDB), p2p list, logs |
| `/mnt/ssd/monero/wallets` | Wallet files (if using wallet RPC) |
| `/mnt/ssd/monero/data/lmdb/` | The actual blockchain database files |

### Useful Commands

```bash
# Check sync status
docker exec monerod monerod status

# Check peer connections
docker exec monerod monerod print_cn

# Check blockchain info
curl -s http://127.0.0.1:18081/get_info | python3 -m json.tool

# Check restricted RPC (from another device)
curl -s http://<node-ip>:18089/get_info | python3 -m json.tool

# Prune an existing full node
docker exec monerod monerod prune_blockchain
```

---

## Appendix B: Security Checklist

- [ ] Restricted RPC only (port 18089) -- never expose full RPC (18081) to the network
- [ ] Wallet RPC bound to localhost only (127.0.0.1:18082)
- [ ] Wallet RPC protected with strong credentials
- [ ] DNS blocklist enabled (`--enable-dns-blocklist`)
- [ ] Tor hidden service for RPC access (no clearnet RPC exposure in sensitive deployments)
- [ ] Docker resource limits enforced
- [ ] Blockchain data on encrypted partition (if device may be captured)
- [ ] Regular Monero software updates (check GitHub releases)
- [ ] Firewall: only ports 18080 (P2P) and 18089 (restricted RPC) open

---

## References

- [Monero Official Documentation](https://docs.getmonero.org/)
- [Monero Tor/I2P Integration Guide](https://docs.getmonero.org/running-node/monerod-tori2p/)
- [Monero Anonymity Networks Documentation (GitHub)](https://github.com/monero-project/monero/blob/master/docs/ANONYMITY_NETWORKS.md)
- [Monero Pruning Explained](https://www.getmonero.org/resources/moneropedia/pruning.html)
- [Monero Multisignature Documentation](https://docs.getmonero.org/multisignature/)
- [Monero Node Requirements 2025 Guide](https://blog.monerica.com/articles/monero-node-requirements)
- [simple-monerod-docker (Seth For Privacy)](https://github.com/sethforprivacy/simple-monerod-docker)
- [Run a Monero Node Guide (Seth For Privacy)](https://sethforprivacy.com/guides/run-a-monero-node/)
- [Monero Wallet RPC Documentation](https://www.getmonero.org/resources/developer-guides/wallet-rpc.html)
- [Monero Multisig Messaging System Guide](https://web.getmonero.org/resources/user-guides/multisig-messaging-system.html)
