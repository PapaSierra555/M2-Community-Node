# Mission 2 - Community Node: Mini-Rack Hardware BOM & Specification

> **Portable 10" Mini-Rack Community Node**
> Inspired by [Jeff Geerling's Project MINI RACK](https://mini-rack.jeffgeerling.com/) -- compact, portable homelabs in a 10" form factor.
>
> **Not building with Pi 5 16GB?** See [BUILD_OPTIONS.md](BUILD_OPTIONS.md) for Pi 4, mini PC, single-device, and no-Monero hardware alternatives.

---

## 1. Bill of Materials - Validation & Expansion

### 1.1 Core Components (User-Specified) - Validation

#### GeeekPi 8U Server Cabinet (DeskPi RackMate T1)
- **Model:** B0CSCWVTQ7 | **Price:** ~$90-100 (Amazon)
- Aluminum alloy + acrylic frame. 16" × 11" × 7.87" (H × W × D). 236.5mm rail spacing. 8U usable.
- **Note:** T1 Plus ($110-120) offers 10.23" depth; standard T1 sufficient for this build.

#### GeeekPi 2U 7.84" Touchscreen
- **Model:** B0F3C5R2BZ | **Price:** ~$65-75 (Amazon)
- 1280×400 LCD capacitive. Connects via HDMI + USB (touch). Draws ~8W; power off to extend UPS runtime.

#### GeeekPi 120mm USB Fan
- **Model:** B0DS2D8M2F | **Price:** ~$12-15 (Amazon)
- L/M/H 3-speed, USB 5V. Shares U8 with LoRa panel — fan on rear rails, panel on front rails. Recommended build uses 2× for push-pull.

#### Raspberry Pi 5 16GB + Active Cooler
- **This build:** Pi 5 16GB board-only (**$205.00 confirmed PiShop.us, Feb 2026**, in stock) + Official Pi 5 Active Cooler (**$10.95 PiShop.us**, in stock). Powered via Anker 747 GaN charger (see §1.2).
- **Note:** CanaKit Starter Kit MAX (B0DRTNTLD5, ~$340) is an alternative bundle but is not the chosen configuration for this build.

#### NVMe SSD for Pi #1 (256GB M.2 2230)
- **Chosen:** WD SN740 256GB M.2 2230 NVMe OEM (ASIN B0C6MVP42M) — **~$35-45 Amazon** — IN STOCK
  - PCIe Gen 4 (throttles to Gen 3 on Pi 5); confirmed Pi 5 compatible.
- **Alternative:** Official Raspberry Pi SSD 256GB (SC1983) — $75 PiShop.us — ⚠️ **OUT OF STOCK Feb 2026**
- **Note:** Enable PCIe Gen 3: add `dtparam=pciex1_gen=3` to `/boot/firmware/config.txt`.

#### NVMe SSD for Pi #2 (1TB M.2 2230)
- **Chosen:** Crucial P310 1TB M.2 2230 NVMe (CT1000P310SSD2) — **~$115-150 Amazon/Newegg/Micro Center** — ✅ IN STOCK
  - PCIe Gen 4 (throttles to Gen 3 on Pi 5); no Pi 5 compatibility issues reported.
- **Alternative:** Official Raspberry Pi SSD 1TB (SC1984) — $120 PiShop.us — ⚠️ **OUT OF STOCK Feb 2026**
- **Performance vs. USB SATA:** 3.5–7× better random IOPS (29K USB → 106K–197K NVMe). Required for Monero LMDB performance.
- **⚠️ Verify price before ordering** — 2230 NVMe prices are volatile due to Steam Deck/handheld demand.

#### TP-Link TL-SG108S 8-Port Gigabit Switch
- **Model:** TL-SG108S | **Price:** ~$26-28 (CompSource ~$26.80 confirmed Feb 2026)
- Unmanaged, fanless, metal housing. Sufficient for this build (router, 2× Pi, touchscreen, 2-3 spare ports).
- **Note:** For VLAN support, TL-SG108E (~$37) adds web UI management — see Premium BOM item 31.

#### 1U Rack Mount for Switch
- **Model:** GeeekPi 1U Shelf (B0D5XMM7HL or similar) | **Price:** ~$15-20 (Amazon)
- Vented cantilever shelf for switch + GL.iNet side by side.

#### 1U Rack PDU (10" Form Factor)
- **Model:** Tupavco TP1713 | **Price:** ~$30-40 (Amazon)
- 4-outlet, surge-protected, 10" form factor. Count AC adapters before ordering — this build uses 2 outlets (GaN charger + switch).
- **Alternative:** DeskPi DC PDU Lite (~$25) — 0.5U DC distribution for SBC builds.

#### Tripp Lite BC600R (600VA/300W) — Recommended UPS
- **Model:** BC600R | **Price:** **~$70 (DigiKey confirmed)** — also Amazon/CDW; verify before ordering
- 600VA/300W. Dimensions: 10.04"×7.09"×2.28" — fits on the RackMate T1 floor, secured with velcro.
- **Runtime:** ~138 min at idle (26W), ~103 min at typical (35W), ~74 min at full load (48.5W).
- **Budget alternative:** Tripp Lite INTERNET350U (~$94.99 Newegg Feb 2026) — 350VA/210W, external only, ~86 min typical.

#### GL.iNet Slate AX (GL-AXT1800)
- **Model:** GL-AXT1800 | **Price:** **$119.99 confirmed (GL.iNet official store, Feb 2026)** — in stock
- WiFi 6, OpenWrt, WireGuard + Tailscale native, IPQ6000 1.2GHz quad-core. Network gateway for the rack.
- **Note:** GL.iNet Flint 2 (~$160) if 2.5GbE or more LAN ports are needed; Slate AX is more portable.

#### Tailscale (Software)
- **Price:** Free (up to 100 devices). Zero-config mesh VPN. Runs on GL.iNet, Pi nodes, and all clients.

---

### 1.2 Recommended Additional Components

#### Raspberry Pi 5 16GB — Node #2 (Dual Pi 5 Build)
- **Price:** **$205.00 confirmed (PiShop.us, Feb 2026)** — in stock
- Broadcom BCM2712 Cortex-A76 4-core 2.4GHz, 16GB LPDDR4X, 2× USB 3.0, 2× USB 2.0, ~3.5W idle / ~10W load.
- Powered via Anker 747 GaN charger (C2 port, 27W). Active Cooler $10.95 PiShop.us.
- **Monero sync:** Initial sync takes 2–4 weeks on ARM natively. Use the **pre-sync workaround** (Phase 0.1): sync LMDB on an x86 machine, rsync to Pi over the network — reduces field-deploy wait to near zero.
- **Note:** GPIO header supports optional Waveshare SX1262 LoRa HAT as alternative to USB radios.

#### GeeekPi 1U Dual Pi 5 Mount (Both Nodes — NVMe Included)
- **Model:** B0F7XBVV4D | **Price:** ~$50-70 (Amazon)
- Mounts both Pi 5s in a single 1U bracket with 2× built-in PCIe→M.2 NVMe adapters (2230/2242/2260/2280). Eliminates a separate M.2 HAT+; saves 1U vs two individual shelves.
- **NVMe performance:** Gen 2 default (~106K IOPS 4K); Gen 3 with `dtparam=pciex1_gen=3` → ~197K IOPS.

#### LoRa Modules for Reticulum/Meshtastic (2× Heltec V3)
- **Heltec WiFi LoRa 32 V3 915MHz × 2** — **$19.90 each confirmed (heltec.org, Feb 2026)** ($26.97 via Rokland US): 50.2×25.5mm, 0.96" OLED, ESP32-S3, USB-C. Both boards are identical hardware — differentiated by firmware and panel position:
  - **LEFT position (ANT 1):** Flash with **RNode firmware** (Mark Qvist / unsigned.io) for Reticulum encrypted mesh transport. → Pi #2 USB 2.0 port 1 (`/dev/ttyUSB0`).
  - **RIGHT position (ANT 2):** Flash with **Meshtastic firmware** for consumer LoRa mesh. → Pi #2 USB 2.0 port 2 (`/dev/ttyUSB1`).
- **Antenna connector:** ⚠️ **IPEX (U.FL) ONLY on both boards** — no SMA connector. Both require U.FL-to-SMA pigtail (item 28) for panel bulkhead connection.
- Both boards mount directly to the custom 1U LoRa panel (item 26) via M2 nylon standoffs (item 28a), with OLEDs aligned behind panel cutout windows. Both assigned to Node #2 — keeps Node #1 (Matrix/Tor/I2P) free of LoRa overhead.
- **Alternative GPIO HAT:** Waveshare SX1262 915M LoRa HAT (~$20-25, Amazon) — if onboard radio preferred over USB.

#### LabStack 2U 80mm Rear Fan Panel (3D Print — Recommended Build)
- **Source:** github.com/JaredC01/LabStack — "2U Mini 2x 80mm Fan Panel" STL
- **Price:** ~$2-3 filament (PETG or PLA+), ~1.5h print; plus ~$15 for 2× 80mm USB 5V fans
- Mounts 2× 80mm fans on **rear** rails at U2-U3, directly behind the Pi 5 node bay. Creates rear exhaust complementing the top 120mm fan — dual exhaust path for sustained-load Pi cooling.
- **Fan spec:** 80mm × 25mm, 5V USB (GDSTIME, ELUTENG, or similar). USB cables route to the USB fan hub at U3 (item 30g).
- Same 10" 236.5mm rail standard as RackMate T1; no modification needed.

#### Micro HDMI to HDMI Cables
- **Price:** ~$8-10 for 2-pack (Amazon). Pi 5 board-only purchase — buy these separately (1ft–2ft).

#### MicroSD Card (Boot Media)
- **Model:** SanDisk Extreme 32GB A2 | **Price:** ~$10-12 (Amazon)
- OS boot and recovery fallback for each Pi. Even with NVMe as primary, keep microSD in slot.

#### Short Ethernet Cables (Cat6, 6-inch to 1-foot)
- **Price:** ~$10-12 for 5-pack (Amazon). Standard cables are too long for a 10" rack.

#### Power Distribution — Anker 747 GaNPrime 150W GaN Charger
- **Model:** Anker 747 GaNPrime 150W, ASIN B09W2PNLX7, ~$65 (Amazon)
- Replaces individual USB-C adapters for both Pi nodes and the GL.iNet. Switch still needs its own 12V DC barrel adapter.
- **Port assignment (4× USB-C + 2× USB-A):**
  - C1 → Pi #1 (27W) | C2 → Pi #2 (27W) | C3 → GL.iNet Slate AX (15W) | C4 → spare
  - USB-A 1 → touchscreen (~8W) | USB-A 2 → 120mm top exhaust fan U8 (~2W)
- **Power pool:** 150W total; simultaneous load ~79W; 71W headroom.
- **PDU outlet usage:** 1 outlet for GaN charger + 1 outlet for switch 12V adapter = 2 of 4 outlets used.
- **⚠️ USB-C cables not included:** Order "USB-C to USB-C, 1ft, 3-pack" separately (~$8–$10) — item 23a in the BOM.
- **Field note:** In solar/LiFePO4 deployments, use a 12V-to-USB-C PD buck converter (one per Pi 5) — no AC inverter needed.

---

## 2. 10" Rack Form Factor Analysis

### 2.1 GeeekPi 8U Cabinet Specifications

| Specification | Value |
|---|---|
| External Dimensions | 16" H x 11" W x 7.87" D |
| Internal Width | ~9.31" (236.5mm between rails) |
| Usable Depth | ~7" (after rail standoff) |
| Usable Height | 8U = 14" (355.6mm) |
| Weight (empty) | ~6 lbs |
| Material | Aluminum alloy frame, acrylic side panels |
| Mounting | Standard 10" rack screw pattern (M6) |

### 2.2 Rack Layout Diagram

#### Front View

```
+==========================================+
|          GeeekPi 8U RackMate T1          |
|          (Front View, Top-Down)          |
+==========================================+
|                                          |
|  U8  [ Custom 1U LoRa Panel (front)  ]   |  <-- 3D print: 2× OLED windows, 2× SMA bulkhead
|      [ Heltec V3 (L) + Heltec V3 (R)]   |     Antennas at top; 120mm fan shares U8 (rear rails)
|                                          |
|  U7  [                               ]   |
|      [ 2U Touchscreen (7.84" LCD)    ]   |  <-- Status dashboard / ATAK map
|  U6  [                               ]   |     HDMI from Pi #1; USB touch to Pi #1
|                                          |
|  U5  [ TP-Link TL-SG108S + GL.iNet  ]   |  <-- Switch + router on shared 1U shelf
|      [ (side by side on 1U shelf)   ]   |
|                                          |
|  U4  [ GeeekPi 1U Dual Pi 5 Mount   ]   |  <-- BOTH Pi 5s in a single 1U bracket
|      [ Pi #1 (Comms)  Pi #2 (TAK)   ]   |     Built-in PCIe NVMe adapters for each
|      [ 256GB NVMe     1TB NVMe      ]   |     Pi #1: Matrix/Tor/I2P | Pi #2: Monero/ATAK
|                                          |
|  U3  [ ---- OPEN ----               ]   |  <-- Available for future expansion
|                                          |
|  U2  [ ---- OPEN ----               ]   |  <-- PDU mounted on REAR rails (see rear view)
|                                          |
|  U1  [ Tripp Lite BC600R (UPS)       ]   |  <-- 600VA/300W; strapped inside rack at U1
|      [ 10.04"x7.09"x2.28"           ]   |     Fits within rack frame; velcro secured
|                                          |
+==========================================+
```

#### Rear View

```
+==========================================+
|          GeeekPi 8U RackMate T1          |
|          (Rear View, Top-Down)           |
+==========================================+
|                                          |
|  U8  [ 120mm USB Fan (rear rails)    ]   |  <-- Shares U8 with LoRa panel (front rails)
|      [ exhaust UP past antennas      ]   |     Open-frame: front+rear coexist at same U
|                                          |
|  U7  [ 2U Touchscreen rear (cables)  ]   |
|  U6  [                               ]   |
|                                          |
|  U5  [ Switch rear ports / GL.iNet   ]   |
|                                          |
|  U4  [ LabStack 2U 80mm Fan Panel    ]   |  <-- 3D print; U4-U3 rear rails
|      [ Fan 1 (80mm USB 5V exhaust)   ]   |     Pull hot Pi air out rearward
|  U3  [ Fan 2 (80mm USB 5V exhaust)   ]   |     Directly behind Pi 5 node bay (U4 front)
|      [ (fan panel continues)         ]   |
|                                          |
|  U2  [ 1U Rack PDU (rear rails)      ]   |  <-- Wings flipped, outlets face INWARD
|      [ outlets → rest on UPS body   ]   |     Adapters sit on BC600R top surface
|                                          |
|  U1  [ UPS rear (wall cable exit)    ]   |  <-- BC600R wall cable exits rear
|                                          |
+==========================================+
```

> **Airflow:** UPS at U1 blocks passive bottom intake — cool air enters from the open-frame sides and rear around U1-U2. 2× 80mm rear fans (U3-U4 rear) actively exhaust Pi node heat (U4 front) rearward → 120mm fan at U8 rear exhausts remaining rising heat upward past the LoRa panel's open sides. The open-frame T1 chassis provides adequate side ventilation even without a dedicated bottom intake panel.
>
> **Front/rear coexistence:** Open-frame RackMate T1 allows simultaneous front and rear mounting at the same U positions. U8: LoRa panel on front rails, 120mm fan on rear rails — no physical conflict. U4-U3: Pi mount on front rails (U4), LabStack 80mm fan panel on rear rails (U4-U3) — directly behind Pi heat source. U3 front is open, allowing the fan panel to extend down unobstructed.

### 2.3 Rack Layout Notes

- **U8 (Top, Front + Rear):** Custom 1U LoRa Panel on **front rails** + 120mm USB fan on **rear rails** — both share U8 via the open-frame chassis. The LoRa panel (3D print, black PETG) mounts both Heltec V3 boards on the panel's interior face using M2 × 8mm nylon standoffs, with their 0.96" OLED screens aligned behind rectangular cutout windows — status visible from the front without opening the rack. Two SMA female bulkhead connectors pass through the panel alongside the OLED windows. Short U.FL-to-SMA-male pigtail cables (6") connect each board's U.FL/IPEX RF connector directly to the interior side of its SMA bulkhead — no jumper cables needed. Both 915 MHz antennas mount externally on the panel bulkheads. The 120mm fan on the rear rails exhausts rising heat upward past the LoRa panel's open sides. **Antennas at the top of the rack for best RF propagation** — maximum height, maximum distance from power cables at U1-U2, and no obstructions above. **The LoRa panel is dedicated to the two LoRa radios only** — the GL.iNet Slate AX uses internal PCB antennas and requires no panel connection. **RF note:** Both LoRa radios are in the 902–928 MHz US915 band; stock defaults (Reticulum ~915.0 MHz, Meshtastic LongFast ~906.875 MHz) are separated by ~8 MHz — no configuration needed unless you change the default channels. WiFi (2.4/5 GHz) and LoRa (915 MHz) have no frequency overlap and coexist without conflict. **USB cable note:** LoRa boards at U8 connect to Pi #2 at U4 — 4U distance requires 3ft USB-C cables (item 23).
- **U7-U6:** The 2U touchscreen is the primary visual interface. Displays Grafana dashboards, ATAK maps, Monero sync status, or system logs. HDMI from Pi #1 (U4), USB touch to Pi #1.
- **U5:** The TP-Link switch (158mm, 6.22" wide) and GL.iNet Slate AX (77mm wide when rotated 90°) share a 1U shelf side by side. Combined width = 235mm in 236.5mm rack interior = **1.5mm clearance — very tight.** ⚠️ **Before assembly: measure your specific shelf's inner usable width.** If the shelf lip reduces usable width below 235mm, place GL.iNet on a small velcro-mount pad beside or behind the switch instead of trying to force side-by-side.
- **U4 (Front):** GeeekPi 1U Dual Pi 5 Mount (B0F7XBVV4D) holds both Pi 5 nodes in a single bracket. Each node gets NVMe via the mount's built-in PCIe adapters — no separate M.2 HAT+ required. This saves 1U compared to the previous 2× separate shelf design. ⚠️ **Before ordering: verify ASIN B0F7XBVV4D on Amazon — confirm product images show: (1) 1U height, (2) two Pi 5 boards installed, (3) two M.2 NVMe adapters, (4) clearance for Official Pi 5 Active Cooler with fan.** This is the critical path item for the entire rack layout.
- **U4-U3 (Rear):** LabStack 2U Mini 2x 80mm Fan Panel (3D print — github.com/JaredC01/LabStack) mounts on the **rear** rails at U4-U3, directly behind the Pi 5 node bay (U4 front). Two 80mm USB 5V fans screw in using their standard coarse-thread screws, oriented to exhaust hot air rearward. USB cables route to the USB fan hub at U3 (item 30g). U3 front is open — no conflict with the fan panel at U3 rear.
- **U3 (Front):** USB fan hub (item 30g) velcroed to interior rail — powers all 3 rack fans from PDU outlet 3 via 5V wall adapter, keeping all Pi USB ports free for field use. Rear side occupied by LabStack fan panel (see above).
- **U2 (Rear):** 1U Rack PDU mounted on **rear rails** with wings/flanges **flipped so outlets face inward** toward the rack interior. This positions the outlets directly above the UPS body at U1 — power adapters (Anker 747 GaN charger, switch 12V barrel adapter, fan hub 5V wall adapter) plug in and rest on top of the BC600R's flat top surface. Result: adapters are supported, contained, and invisible from both front and rear. Ultra-short PDU-to-UPS cable run (1U). U2 front is open. Outlet allocation: (1) Anker 747 → USB-C power to Pis, GL.iNet, touchscreen; (2) Switch 12V barrel; (3) fan hub 5V adapter; (4) spare.
- **U1 (Front):** Tripp Lite BC600R (10.04"×7.09"×2.28") sits inside the rack at U1. The UPS footprint (10.04"×7.09") fits within the rack's 11"×7.87" frame. ⚠️ **Verify in person:** The BC600R's 2.28" height is ~1.3U — it will protrude slightly above the U1 boundary into U2 space. Ensure no physical conflict with the PDU at U2. Secure with velcro to the rack frame. Wall outlet cable exits the rear; PDU 6ft cable connects UPS output to PDU at U2 (just 1U above — minimal cable length needed).
- **Hardware aesthetics:** The RackMate T1 ships with silver/zinc rack screws. For a fully matched black build, replace all panel mounting screws with **M6 × 10mm black button head socket cap screws** (item 30d) and 80mm fan mounting screws with **M3 × 25mm black socket cap** (item 30e). Print the custom LoRa panel and LabStack rear fan panel in black PETG (item 30f). The result is an all-black hardware profile — no silver visible on the front or rear of the rack.

### 2.4 USB Port Budget

Pi 5 has 4 USB ports: 2× USB 3.0 + 2× USB 2.0. All 3 rack fans are powered by the USB fan hub (item 30g) at U3 — **not** from Pi USB ports — keeping Pi front panels clean for field use.

| Pi | USB 3.0 Port 1 | USB 3.0 Port 2 | USB 2.0 Port 1 | USB 2.0 Port 2 | Spare |
|---|---|---|---|---|---|
| Pi #1 (comms) | Free | Free | Touchscreen touch input | Free | 2× USB 3.0 + 1× USB 2.0 |
| Pi #2 (tactical) | Free | Free | Heltec V3 — LEFT (RNode) | Heltec V3 — RIGHT (Meshtastic) | **2× USB 3.0** |

> **Fan power:** All 3 fans (120mm + 2× 80mm) plug into the USB fan hub at U3 (item 30g), powered by a 5V wall adapter on PDU outlet 3. This keeps Pi USB ports free for field peripherals (debug probes, cellular modems, USB drives, etc.).

> **Cellular modem note:** The cellular modem (Premium add-on Quectel RM520N-GL) connects to the **GL.iNet router's USB 3.0 port** — not to Pi #2.

### 2.5 Cable Management

- Use 6" Cat6 patch cables between switch, Pi nodes, and GL.iNet router
- Route USB and HDMI cables behind the SBC shelves (7.87" depth provides ~1" behind components)
- Use Velcro cable ties (not zip ties) for easy reconfiguration
- Label all cables with color or numbered tags
- Power cables from PDU route down the right rail

---

## 3. Power Budget Calculation

### 3.1 Component Power Draw

| Component | Idle (W) | Load (W) | Notes |
|---|---|---|---|
| Raspberry Pi 5 16GB #1 | 3.5 | 10.0 | Matrix, Tor, I2P, containers |
| Raspberry Pi 5 16GB #2 | 3.5 | 10.0 | Monero, ATAK, Reticulum |
| TP-Link TL-SG108S | 3.5 | 3.5 | Constant draw, no PoE |
| GL.iNet Slate AX | 5.0 | 7.0 | WiFi 6 AP + WireGuard active |
| GeeekPi 7.84" Touchscreen | 6.0 | 8.0 | LCD backlight + touch controller |
| WD SN740 256GB NVMe (Pi #1 via GeeekPi mount PCIe) | 0.8 | 1.8 | M.2 2230, PCIe Gen 3/4; lower than USB SATA |
| Crucial P310 1TB NVMe (Pi #2 via GeeekPi mount PCIe) | 1.0 | 2.2 | M.2 2230, PCIe Gen 4→3 on Pi 5; replaces USB SATA |
| 120mm USB Fan (U8 rear rails) | 1.5 | 2.0 | Medium speed setting |
| 2x 80mm USB Fans (rear exhaust, U4-U3 rear) | 1.0 | 1.5 | ~0.5W each at medium; powered via USB fan hub at U3 |
| 2× Heltec V3 (USB LoRa, Pi #2) | 0.2 | 0.8 | Two USB LoRa on Pi #2 USB 2.0 ports (serial 115200 baud — USB 2.0 is sufficient) |
| **TOTAL** | **~26W** | **~48.5W** | Dual exhaust (top + rear) for active Pi node cooling |

### 3.2 UPS Runtime Analysis

#### Tripp Lite BC600R (600VA / 300W) — Recommended; Rack-Floor Mounted
- Battery: ~6Ah at 12V = 72Wh usable (~60Wh after efficiency losses)
- Price: **~$70 (DigiKey confirmed; verify Amazon before ordering)**
- Dimensions: 10.04"×7.09"×2.28" — sits inside rack at U1; secured with velcro to rack frame
- **At idle load (26W):** ~60Wh / 26W = **~138 minutes (2 hr 18 min)**
- **At typical load (35W):** ~60Wh / 35W = **~103 minutes (1 hr 43 min)**
- **At full load (48.5W):** ~60Wh / 48.5W = **~74 minutes (1 hr 14 min)**
- **Key advantage:** Self-contained at U1 inside rack — no external UPS needed. All power infrastructure in one portable unit.

#### Budget Option: Tripp Lite INTERNET350U (350VA / 210W) — External
- Battery: ~5Ah at 12V = 60Wh usable (~50Wh after efficiency losses)
- Price: **~$94.99 confirmed (Newegg, Feb 2026)**
- **At idle load (26W):** ~115 minutes | **At typical (35W):** ~86 minutes | **At full (48.5W):** ~62 minutes
- **Note:** Does NOT fit inside rack; must sit external. Use only if BC600R is unavailable.

### 3.3 Power Recommendation

| Scenario | UPS Recommendation |
|---|---|
| Standard deployment (recommended) | Tripp Lite BC600R — U1 inside rack, self-contained |
| Vehicle (12V inverter available) | BC600R as buffer; 12V inverter is primary |
| Field (battery/solar only) | Skip UPS entirely; use LiFePO4 battery + DC-DC converters |
| Budget / BC600R unavailable | Tripp Lite INTERNET350U (external placement) |

**For field deployment beyond 3 hours:** Use LiFePO4 battery (12V 100Ah = 1.2kWh) with 12V-to-USB-C PD DC-DC converters — far more efficient than UPS chemistry.

**Power-saving tip:** `vcgencmd display_power 0` turns off the touchscreen (saves 6-8W, adds ~15-20 min to BC600R runtime). Script on a UPS battery-low signal if possible.

### 3.4 Power-Saving Tips
- Set Pi 5 CPU governor to `powersave` when idle
- Disable GL.iNet WiFi in wired-only scenarios
- Put LoRa in receive-only mode (0.1W vs 0.5W transmit)

---

## 4. GL.iNet Slate AX as Network Core

### 4.1 Specifications

| Feature | Detail |
|---|---|
| CPU | Qualcomm IPQ6000, 1.2GHz quad-core |
| RAM | 512MB DDR3L |
| Flash | 128MB NAND |
| WiFi | WiFi 6 (802.11ax), 2.4GHz + 5GHz |
| Antennas | Internal PCB antennas (2.4 GHz + 5 GHz) — no external connectors; no modification needed or recommended |
| Ethernet | 1x WAN (1GbE), 2x LAN (1GbE) |
| USB | 1x USB 3.0 |
| VPN | WireGuard, OpenVPN (client & server) |
| OS | OpenWrt (GL.iNet fork) |
| Power | USB-C, 5V/3A (15W max, ~7W typical) |
| Size | 4.6" x 3" x 1.1" |

### 4.2 Configuration Recommendations

1. **DHCP Server:** GL.iNet runs DHCP on 192.168.8.0/24 (default) or custom subnet. Assign static leases for Pi 5 nodes.
2. **WiFi AP:** Broadcast community SSID for local device access. Use WPA3 if supported by client devices.
3. **WireGuard Server:** Built-in WireGuard server enables remote access without Tailscale dependency.
4. **Tailscale:** Native Tailscale package available in GL.iNet firmware. Enables zero-config remote access from any device running Tailscale.
5. **DNS Filtering:** Built-in AdGuard Home for DNS-level ad/tracker blocking.
6. **Firewall:** OpenWrt-based firewall isolates WAN from LAN. Configure port forwarding only for services that need external access.

### 4.3 Uplink Options

| Scenario | Uplink Method |
|---|---|
| Home/Office | Ethernet WAN to existing router/modem |
| Hotel/Public WiFi | Repeater mode (WiFi WAN to WiFi LAN) |
| Vehicle/Field | USB tethering from phone, or USB cellular modem |
| Remote site | Starlink/cellular hotspot to WAN port |

### 4.4 Firmware

- **GL.iNet Official Firmware (recommended):** Includes admin panel, Tailscale, AdGuard Home, VPN management. Regular security updates.
- **Stock OpenWrt:** Loses GL.iNet admin panel. Only use if you need unavailable packages.

---

## 5. Storage Architecture

### 5.1 Drive Assignments

| Drive | Interface | Capacity | Assigned Workloads |
|---|---|---|---|
| microSD (Pi #1 boot) | SD slot | 32GB | Pi OS boot partition, recovery |
| NVMe SSD (Pi #1) | M.2 NVMe (PCIe, GeeekPi dual mount) | 256GB | Mounted at /mnt/nvme — Docker volumes, Matrix DB, service data. OS stays on microSD. |
| microSD (Pi #2 boot) | SD slot | 32GB | **OS boot and root filesystem for Pi #2** — OS stays on microSD; NVMe is data only |
| NVMe SSD (Pi #2) | M.2 NVMe (PCIe, GeeekPi dual mount) | 1TB | Monero blockchain (~95GB pruned), ATAK data, backups — mounted at /mnt/nvme; not the root OS |

### 5.2 Partitioning Recommendations

#### NVMe 256GB (Pi 5 #1 - Primary Services)
```
/dev/nvme0n1p1    256MB   /boot/firmware   (FAT32, boot partition)
/dev/nvme0n1p2     50GB   /                (ext4, root filesystem)
/dev/nvme0n1p3    190GB   /srv             (ext4, service data - Matrix DB, ATAK, Docker)
(~16GB unpartitioned for wear leveling / overprovisioning)
```

#### NVMe 1TB (Pi 5 #2 — via GeeekPi Dual Mount PCIe Adapter)
```
/dev/nvme0n1p1    256MB   /boot/firmware   (FAT32 — if migrating OS to NVMe; otherwise omit)
/dev/nvme0n1p2     50GB   /                (ext4 — if migrating OS to NVMe; otherwise omit)
/dev/nvme0n1p3    900GB   /mnt/nvme        (ext4, Monero LMDB, ATAK data, backups)
(~50GB unpartitioned for wear leveling)
```

> **Recommended:** Keep Pi #2 OS on microSD; NVMe is data-only. Simpler, provides fallback boot, no EEPROM changes needed. Migrate OS to NVMe later after build is stable. See Build Guide §5.1.

### 5.3 Backup Strategy

1. **Config Backup:** Cron job rsync critical configs from NVMe to /mnt/backup on SATA SSD daily
2. **Monero Wallet:** Encrypt wallet keys, store backup on separate USB drive kept offline
3. **Matrix Data:** Export room keys periodically; database dump to /mnt/backup weekly
4. **Full Image Backup:** Monthly `dd` image of NVMe to external USB drive (keep offsite)
5. **Recovery:** Boot from microSD, mount NVMe/SATA, restore from backup partition

---

## 6. Thermal Management

### 6.1 Heat Sources

| Component | Max TDP | Location |
|---|---|---|
| Pi 5 #1 (under load) | 10W | U4 |
| Pi 5 #2 (under load) | 10W | U4 |
| Touchscreen backlight | 8W | U7-U6 |
| TP-Link switch | 3.5W | U5 |
| GL.iNet router | 7W | U5 |
| **Total heat in enclosure** | **~39W** | |

### 6.2 Cooling Strategy

```
    FRONT                                     REAR
    +-----------+                             +-----------+
    U8  | LoRa Pnl  |  (antennas at top)     | 120mm Fan |  ^  ^  ^ (exhaust up)
    +-----------+                             +-----------+
    U7-6| Touchscr. |                        | screen rear|
    U5  |  Switch   |                        | switch rear|
    U4  | Dual Pi   |  ===================> | [80mm Fan1]| Pi node heat
        | Mount     |   Pi generates heat    | [80mm Fan2]| exits rearward
    U3  |  (open)   |                        | (fan cont.)|
    U2  |   PDU     |                        |  PDU rear  |
    U1  |   UPS     |                        | UPS rear   |
    +-----------+                             +-----------+
         ^  ^  ^
         |  |  |   (cool air enters around UPS sides)
    [BC600R UPS — U1 front, open-frame sides]
```

- **Primary exhaust:** 120mm USB fan at U8 **rear rails**, shares U8 with LoRa panel on front rails. Exhausts rising heat upward past the antennas. The LoRa panel's open sides and the open-frame chassis allow air to escape freely.
- **Secondary exhaust:** 2× 80mm USB fans in LabStack rear panel at U4-U3 (rear rails), directly behind the Pi 5 node bay (U4 front) — pulls Pi heat out rearward before it rises; most effective cooling path for the Pi nodes
- **Intake:** Open-frame T1 chassis allows cool air to enter around the sides and bottom of the UPS at U1. The BC600R does not seal the bottom; ambient air moves upward naturally through the open frame.
- **Component-level:** Pi 5 Active Cooler (official) on each node — heatsink + PWM fan controlled by Pi firmware
- **Monitoring:** `vcgencmd measure_temp` on each Pi 5, with alerts at 70°C (warning) and 80°C (throttle)

### 6.3 Temperature Thresholds

| Temperature | Pi 5 Behavior |
|---|---|
| < 60C | Normal operation |
| 60-80C | Fan ramps up (PWM active cooling) |
| 80C+ | CPU thermal throttling begins |
| 85C+ | Aggressive throttling, performance severely degraded |

### 6.4 Field Deployment Thermal Concerns

| Environment | Risk | Mitigation |
|---|---|
| Indoor (air-conditioned) | Low | Single exhaust fan sufficient |
| Indoor (no AC, summer) | Medium | Dual fan push-pull, reduce CPU clock if needed |
| Vehicle (summer, parked) | HIGH | Never leave powered on in parked vehicle in sun. Interior temps can exceed 60C |
| Outdoor (shade) | Medium | Ensure airflow; ambient up to 40C is manageable with active cooling |

### 6.5 Operating Temperature Range
- **Recommended:** 0C to 40C ambient (32F to 104F)
- **Maximum:** -10C to 50C with active cooling and thermal throttling accepted
- **Storage:** -20C to 60C (powered off)

---

## 7. Field Deployment Scenarios

### 7.1 Indoor Deployment (Primary Use Case)

**Setup:** Plug into wall power, connect Ethernet uplink to existing network.

| Item | Detail |
|---|---|
| Power | Wall outlet -> UPS -> PDU -> all components |
| Network | Ethernet from home/office router -> GL.iNet WAN port |
| WiFi | GL.iNet broadcasts community SSID for local access |
| Remote Access | Tailscale mesh VPN for off-site management |
| Setup Time | ~15 minutes (plug in, power on, verify services) |

### 7.2 Vehicle Deployment

**Setup:** 12V vehicle power, cellular uplink.

| Item | Detail |
|---|---|
| Power | 12V cigarette lighter -> 150W inverter -> UPS -> PDU |
| Alternative Power | 12V -> USB-C PD car charger (direct to Pi, bypass UPS) |
| Network | USB cellular modem or phone USB tethering -> GL.iNet |
| Mounting | Secure rack with bungee cords or ratchet straps to cargo area |
| Setup Time | ~10 minutes (already configured, just power on) |

**Additional Hardware for Vehicle:**
- 150W pure sine wave inverter (~$30)
- 12V to USB-C PD adapter, 27W+ (~$15)
- USB cellular modem (Quectel RM520N-GL, ~$80) or phone tethering (free)

### 7.3 Solar/Battery Field Deployment

**Setup:** Off-grid, solar + battery, 24-hour autonomous operation.

**Power Budget for 24 Hours:** Typical load ~35W × 24h = 840Wh; with 20% losses = ~1,010Wh required.

**Recommended Solar/Battery Kit:**
| Component | Specification | Price |
|---|---|---|
| LiFePO4 Battery | 12V 100Ah (1,280Wh) | ~$200-300 |
| Solar Panel | 100W monocrystalline, portable/foldable | ~$80-120 |
| Solar Charge Controller | 20A MPPT | ~$40-60 |
| 12V to 5V DC-DC Converter | Buck converter, 10A, USB-C PD output | ~$15-25 |
| Total Solar Kit | | ~$335-505 |

Skip the UPS in solar deployment — the LiFePO4 battery serves as UPS. Use 12V-to-USB-C PD DC-DC converters directly to Pi nodes.

### 7.4 Transport & Protection

| Item | Recommendation | Price |
|---|---|---|
| Carrying Case | **Pelican 1610** (21.78"×16.69"×10.62" interior) | $180–$220 |
| Foam Insert | Custom-cut kaizen foam, 2" thick, cut to rack profile | $20 |
| Cable Bag | Small zippered pouch for spare cables, SD cards | $5–$10 |

> **Case sizing note:** The RackMate T1 must be transported laid flat on its side. Laid flat, the rack occupies 16"L × 11"W × 7.8"H inside the case (depth = rack body depth). The Pelican 1610 provides ~2.8" of depth clearance for foam padding. With the BC600R UPS inside the rack at U1, the rack is a self-contained unit (~16" assembled length) and fits easily with ample clearance.
>
> ⚠️ **Apache 4800 does NOT fit.** Its interior is only 7.25" deep — the rack is 7.8" deep. Fails by 0.55" before even accounting for foam. Apache 5800 (5.69" deep) and Pelican 1510 (7.6" deep, zero width clearance) also do not fit.

**Setup Time Estimates:**
| Scenario | Time from Bag to Operational |
|---|---|
| Indoor (pre-configured) | 10-15 minutes |
| Vehicle | 5-10 minutes |
| Solar/battery field | 30-45 minutes (includes solar panel setup) |

---

## 8. Final Complete BOM with Pricing

### 8.1 Budget Build (Single Pi 5, Minimal Extras)

> **Availability note (Feb 2026):** GeeekPi RackMate T1 and 2U Touchscreen were SOLD OUT at DeskPi.com. Check Amazon ASINs B0CPLRD29P and B0F3C5R2BZ. Prices shown are as-of Feb 2026; verify all prices before ordering.

| # | Component | Model | Price | Source | Notes |
|---|---|---|---|---|---|
| 1 | 10" 8U Rack Cabinet | GeeekPi DeskPi RackMate T1 | $119.99 | Amazon (B0CPLRD29P) | SOLD OUT at DeskPi; check Amazon |
| 2 | 2U Touchscreen | GeeekPi 7.84" 1280x400 LCD | $79.99 | Amazon (B0F3C5R2BZ) | SOLD OUT at DeskPi; check Amazon |
| 3 | 120mm USB Fan | GeeekPi RackMate Fan | $13 | Amazon | 3-speed switch |
| 4 | Pi 5 16GB Board | Raspberry Pi 5 16GB | $205.00 | PiShop.us | Confirmed in stock Feb 2026 |
| 4a | Pi 5 Active Cooler | Official Raspberry Pi Active Cooler | $10.95 | PiShop.us | Confirmed in stock |
| 4b | USB-C PSU 27W | USB-C PD 27W adapter | $12 | Amazon | 5V/5A; required for Pi 5 |
| 5 | 1TB SATA SSD | Crucial BX500 CT1000BX500SSD1 | $123.99 | Newegg | Confirmed Feb 2026 |
| 6 | USB-SATA Adapter | SABRENT EC-SSHD | $10 | Amazon | USB 3.0 to 2.5" SATA |
| 7 | 8-Port Switch | TP-Link TL-SG108S | $27 | Amazon/Newegg | ~$26-28 confirmed Feb 2026 |
| 8 | 1U Switch Shelf | GeeekPi 1U Vented Shelf | $17 | Amazon | Cantilever tray |
| 9 | 1U Rack PDU | Tupavco TP1713 | $35 | Amazon | 4 outlet, surge protection |
| 10 | UPS | Tripp Lite INTERNET350U | $94.99 | Newegg | Confirmed Feb 2026; 350VA/210W |
| 11 | Travel Router | GL.iNet Slate AX (AXT1800) | $119.99 | GL.iNet store | Confirmed in stock Feb 2026 |
| 12 | MicroSD Card | SanDisk Extreme 32GB A2 | $10 | Amazon | Boot/recovery media |
| 13 | Short Ethernet Cables | Cat6 6" 5-pack | $10 | Amazon | Rack cable management |
| | | | **~$889** | | Prices confirmed Feb 2026 |

### 8.2 Recommended Build (Dual Pi 5, NVMe Both Nodes, USB LoRa)

> **Availability note (Feb 2026):** RackMate T1 and 2U Touchscreen were SOLD OUT at DeskPi.com — check Amazon ASINs. Official Pi SSDs were OUT OF STOCK at PiShop.us — use WD SN740 (Pi #1) and Crucial P310 (Pi #2) as shown below. **Verify all prices before ordering** — 2230 NVMe market is volatile due to handheld gaming demand; tariff disruption may affect all prices as of March 2026.

| # | Component | Model | Est. Price | Source | Notes |
|---|---|---|---|---|---|
| 1 | 10" 8U Rack Cabinet | GeeekPi DeskPi RackMate T1 | $119.99 | Amazon B0CPLRD29P | SOLD OUT DeskPi; check Amazon |
| 2 | 2U Touchscreen | GeeekPi 7.84" 1280x400 LCD | $79.99 | Amazon B0F3C5R2BZ | SOLD OUT DeskPi; check Amazon |
| 3 | 120mm USB Fan x2 | GeeekPi RackMate Fan | $26 | Amazon | Push-pull airflow ($13 ea.) |
| 4 | Pi 5 16GB Board #1 | Raspberry Pi 5 16GB | $205.00 | PiShop.us | Node #1: Matrix, Tor, I2P; confirmed in stock |
| 5 | Pi 5 Active Cooler #1 | Official Raspberry Pi Active Cooler | $10.95 | PiShop.us | Confirmed in stock Feb 2026 |
| 6 | Pi 5 16GB Board #2 | Raspberry Pi 5 16GB | $205.00 | PiShop.us | Node #2: Monero, ATAK, Reticulum |
| 7 | Pi 5 Active Cooler #2 | Official Raspberry Pi Active Cooler | $10.95 | PiShop.us | Confirmed in stock Feb 2026 |
| 8 | 1U Dual Pi Mount + NVMe | GeeekPi Dual Pi 5 Mount B0F7XBVV4D | ~$60 | Amazon | Both Pi 5s in 1U; includes 2× PCIe NVMe adapters |
| 9 | Pi #1 NVMe SSD 256GB | WD SN740 256GB M.2 2230 OEM | ~$40 | Amazon B0C6MVP42M | Verify price; Official Pi SSD 256GB OOS ($75 PiShop) |
| 10 | Pi #2 NVMe SSD 1TB | Crucial P310 1TB M.2 2230 CT1000P310SSD2 | ~$115-150 | Amazon/Newegg/Micro Center | In stock Feb 2026; verify current price |
| 11 | GaN Multi-Port Charger | Anker 747 GaNPrime 150W (B09W2PNLX7) | ~$65 | Amazon | 150W pool; C1→Pi#1 (27W), C2→Pi#2 (27W), C3→GL.iNet (15W), USB-A→display; 2 PDU outlets total |
| 12 | 8-Port Switch | TP-Link TL-SG108S | $27 | Amazon/Newegg | ~$26-28 confirmed Feb 2026 |
| 13 | 1U Switch Shelf | GeeekPi 1U Vented Shelf | $17 | Amazon | Switch + GL.iNet side by side |
| 14 | 1U Rack PDU | 10" Rack PDU 1U 4-Outlet (B0FP56YSWZ) | ~$35 | Amazon | 4-outlet, 125V/15A, surge protection, 6ft cable, metal housing |
| 15 | UPS | Tripp Lite BC600R 600VA | ~$70 | DigiKey/Amazon | **U1 inside rack**, secured with velcro; 10.04"×7.09"×2.28" (~1.3U height) |
| 16 | Travel Router | GL.iNet Slate AX (AXT1800) | $119.99 | GL.iNet store | Confirmed in stock Feb 2026 |
| 17 | LoRa USB — RNode | Heltec WiFi LoRa 32 V3 915MHz | $19.90 | heltec.org | **LEFT position on panel**; flash with RNode firmware for Reticulum |
| 18 | LoRa USB — Mesh | Heltec WiFi LoRa 32 V3 915MHz | $19.90 | heltec.org | **RIGHT position on panel**; flash with Meshtastic firmware |
| 19 | LoRa Antennas | 915 MHz SMA antennas, 2-pack | $12 | Amazon | ⚠️ **Must be SMA male connector (NOT RP-SMA)**. The SMA female bulkhead on the custom LoRa panel requires SMA male on the antenna. RP-SMA looks identical but won't mate. Verify connector type in listing photos before ordering. |
| 20 | MicroSD Card x2 | SanDisk Extreme 32GB A2 | $20 | Amazon | Boot/recovery for both Pi nodes ($10 ea.) |
| 21 | Short Ethernet Cables (internal) | Cat6 6" 5-pack | $10 | Amazon | Rack-internal connections: switch↔Pi#1, switch↔Pi#2, switch↔GL.iNet, switch↔touchscreen, +1 spare |
| 21a | WAN Ethernet Cable | Cat6 3ft or 6ft, 1× | ~$5 | Amazon | GL.iNet WAN port → uplink (home router, Starlink, etc.). 6" patch cables are too short for this run. |
| 22 | Micro HDMI Cables | 2-pack, 1ft–2ft | $8 | Amazon | **Cables, not adapter dongles.** Micro HDMI male → HDMI male. Need ~18"–24" length to reach from Pi mount (U3) to touchscreen (U6-U7) via cable routing path. 2ft recommended. For initial setup of each Pi also useful. |
| 23 | USB-A to USB-C Cables | 3ft, 2-pack | $8 | Amazon | LoRa radios (U8) to Pi #2 USB 3.0 ports (U4) — 4U distance requires 3ft cables. Route via right rail. |
| 23a | USB-C to USB-C Cables | 1ft, 3-pack | ~$9 | Amazon | **Missing from original BOM.** Pi #1 power (Anker C1), Pi #2 power (Anker C2), GL.iNet power (Anker C3). Anker 747 does NOT include 3 cables. |
| 24 | Velcro Cable Ties | 50-pack | $6 | Amazon | Cable management + UPS floor straps |
| 24a | Cable Labels | P-Touch label tape or pre-printed cable ID tags | ~$6 | Amazon | Build guide §1.5 requires labeling both ends of every cable. Brady or Dymo label tape works; masking tape + sharpie is acceptable. |
| 25 | *(removed — UPS occupies U1; no vented blank needed)* | — | — | — | BC600R UPS at U1 replaces the vented blank. Open-frame chassis provides adequate bottom intake around UPS sides. |
| 26 | Custom 1U LoRa Panel | 1U 10" rack panel with 2× OLED windows, 2× SMA bulkheads, 2× M2 board mounts (3D print) | ~$2 | Custom STL (design in §1.3) | **U8 front rails** — shares U8 with 120mm fan on rear rails. Antennas at maximum height for best RF propagation. Black PETG; mounts both LoRa boards behind OLED cutouts with SMA feedthroughs to external antennas. |
| 27 | SMA Bulkhead Connectors | SMA Female Panel Mount, 4-pack | ~$8 | Amazon | 2 used at U2 panel; feedthrough with nut |
| 28 | U.FL-to-SMA Pigtails | U.FL (IPEX MHF4) to SMA Male, 6", 2-pack | ~$8 | Amazon | Board U.FL connector → SMA female bulkhead interior (direct connection, no jumper needed). Both Heltec V3 boards use U.FL/IPEX on-board connectors (IPEX only — no SMA on board). |
| 28a | M2 Nylon Standoff Kit | M2 × 8mm nylon standoffs + M2 × 5mm screws, 20-pack | ~$3 | Amazon | Mount both Heltec V3 boards to custom LoRa panel. 4 standoffs per board = 8 used. Nylon prevents shorts on bare PCB underside. |
| 29 | LabStack Rear Fan Panel | 2U Mini 2x 80mm Fan Panel (3D print) | ~$2 | github.com/JaredC01/LabStack | **U4-U3 rear rails** — directly behind Pi mount (U4 front); U3 front is open, no conflict; uses fans' coarse-thread screws |
| 30 | 80mm USB Fans | AC Infinity MULTIFAN S5 (B00IJ2J2K0) | ~$16 | Amazon | Dual 80mm, 5V USB, inline speed switch, UL-certified. Rear exhaust; screw into LabStack panel with included screws. |
| 30a | *(removed — fan hub eliminates direct Pi fan connections; extension no longer needed)* | — | — | — | — |
| 30g | USB Fan Hub Kit | 4-port USB-A hub + 5V/2A USB wall adapter | ~$13 | Amazon | Powers all 3 rack fans (120mm + 2× 80mm) from PDU outlet 3. Velcro-mount at U3 interior. Keeps all Pi USB ports free for field use. Hub at U3 = short cable runs to 80mm fans (U3-U4 rear) and 120mm fan (U8 rear). |
| 30b | *(removed — custom LoRa panel has no keystone slots)* | — | — | — | — |
| 30c | Dust Filter Foam | 120mm foam filter pad, 2-pack | ~$5 | Amazon | Cut to fit open-frame intake areas around UPS at U1. Prevents dust accumulation on Pi 5 Active Cooler fins during continuous operation. Replace every 3–6 months. |
| 30d | Black Rack Screws + Cage Nuts | M6 × 10mm Button Head Socket Cap, Black Oxide + M6 Cage Nuts, 50-pack combo | ~$10 | Amazon | ⚠️ **Verify M5 vs M6 from your actual T1 unit before ordering** — check the included hardware bag. Button head hex drive looks cleanest; pan head Phillips is the budget alternative. Need ~40 total: 8U front panels (32) + 2U rear fan panel (8). T1 includes some silver screws — replace all for uniform black look. |
| 30e | Black Fan Screws | M3 × 25mm Socket Cap, Black Oxide, 20-pack | ~$6 | Amazon | 80mm fans mount to LabStack rear fan panel with 4 screws each = 8 needed. Fans include silver screws — swap for black. M3 × 25mm passes through fan body into 3D printed panel; verify thread engagement is ≥5mm. |
| 30f | Black PETG Filament | Black PETG, 1kg spool | ~$20 | Amazon / Hatchbox / Polymaker | Print custom 1U LoRa panel (item 26) and LabStack rear fan panel (item 29) in black PETG to match rack hardware. PETG preferred over PLA — better heat tolerance in enclosed rack. If you already have black PETG, no extra cost. |
| | | | **~$1,385–$1,425** | | ⚠️ Verify SSD prices before ordering — 2230 NVMe volatile |

### 8.3 Premium Build (Managed Switch, Second SSD, Cellular, Case)

| # | Component | Model | Est. Price | Source | Notes |
|---|---|---|---|---|---|
| 1-30 | All Recommended Build items | (see above) | ~$1,385–$1,425 | | |
| 31 | Switch Upgrade (replaces #12) | TP-Link TL-SG108E (managed) | +$10 | Amazon | VLAN support, QoS, port mirroring via web UI; ~$37 vs $27 net |
| 32 | Expansion USB SSD | Samsung T7 1TB USB 3.2 | ~$90 | Amazon | Portable USB SSD for Pi #2 backups/overflow; no adapter needed |
| 33 | USB Cellular Modem | Quectel RM520N-GL (5G) | $85 | Amazon | Field cellular backhaul |
| 34 | Carrying Case | Pelican 1610 Protector Case | $180–$220 | Amazon / Pelican direct | Interior 21.78"×16.69"×10.62". T1 rack (11"W×7.8"D×16"H) laid flat = 16"L×11"W×7.8"H; fits with ~2.8" depth clearance and 5"+ width clearance. Rack+BC600R assembled (~18.3"L) also fits with 3.5" spare. ⚠️ **Apache 4800 does NOT fit** — only 7.25" interior depth vs 7.8" rack depth. |
| 35 | Kaizen Foam Insert | 2" thick, custom-cut | $20 | Amazon | Cut to rack profile for shock protection; ~1.4" on each rack face |
| | | | **~$1,705–$1,785** | | ⚠️ Verify all prices before ordering |

### 8.4 Field Operations Kit — Disaster Recovery (Pelican Case Pack-In)

These items live permanently inside the Pelican 1610 case — packed in the lid mesh pocket and a small zip pouch beside the rack. Goal: fix the most likely field failures on-site without returning to base.

#### Failure Tiers

| Tier | Likely Failures | Field-Fixable? |
|---|---|---|
| 1 (common) | Cable failure, loose antenna, OS/config corruption | Yes — spare cables + recovery USB |
| 2 (less common) | LoRa module failure, router soft-brick, charger failure | Yes — spare module + backup charger |
| 3 (rare) | Pi 5 board failure, NVMe hardware failure, UPS battery | No — return to base for swap |

#### Field Kit BOM

| # | Category | Component | ASIN | Cost | Notes |
|---|---|---|---|---|---|
| 36 | Cables | USB-C 100W cable, 2-pack (6ft) | B09JFF1PPK | ~$12 | Anker; powers Pi 5s from Anker 747 — first thing to fail in field; carry 2 |
| 37 | Cables | USB-C to USB-A cable (3ft) | — | ~$6 | Recovery/flashing use; any quality brand |
| 38 | Cables | Cat6 1ft patch cable, 6-pack, black | B0FXWWDVBJ | ~$12 | CableGeeker; rack internal runs are short — carry a full pack |
| 39 | RF | 915MHz SMA male antenna, 2x spare | — | ~$10 | Same spec as LoRa panel antennas; must remove before packing case; these are what you'll snap or lose first |
| 40 | Diagnostics | USB-C inline power meter, 2-pack (240W) | B0D8PJ46WV | ~$12 | LED V/A/W display; inline between charger and Pi; isolates cable vs charger vs Pi failure in 30 seconds |
| 41 | Power | 65W GaN USB-C charger, single port, black | B087MFLLCR | ~$30 | Amazon Basics GaN; backup if Anker 747 fails; runs GL.iNet + one Pi at full load; foldable plug |
| 42 | Spare Parts | Heltec WiFi LoRa 32 V3, 915MHz (1x) | B0CW6151WJ | ~$25 | 2-pack listing; use 1 as hot spare, keep 2nd at base; if RNode dies mesh comms stop |
| 43 | Tools | iFixit Mako 64-bit precision driver kit | B0189YWOIO | ~$30 | PH0/PH1, Torx, hex — covers every screw in the rack; magnetic; fits in zip pouch |
| 44 | Tools | Anti-static wrist strap (iFixit) | B00B2T9C8Y | ~$8 | ESD protection for Pi/NVMe swap in field; clip to rack chassis as ground point |
| 45 | Recovery | USB-A flash drive, 32GB+ | — | ~$10 | Pre-loaded: Pi OS image (current pinned), docker-compose + .env backups, SSH key (encrypted), RECOVERY.md; refresh before each deployment |
| 46 | Recovery | microSD card, 32GB Class 10, pre-flashed | — | ~$8 | Fallback boot if NVMe fails; flash Raspberry Pi OS Lite ARM64 + SSH enabled; test boot before packing |

**Field Kit Subtotal: ~$165–$175**

> **Packing:** Items 36–40, 43–46 fit in one small zip pouch (lid mesh pocket). Item 41 (charger) and item 42 (Heltec spare) pack beside the rack in side foam. Antennas (item 39) wrap in foam pocket or cable bag — they must be removed from the LoRa panel before closing the case.

> **Recovery USB prep:** Before each deployment, verify the USB stick has current config backups. Run `tar -czf backup-$(date +%Y%m%d).tar.gz /opt/community-node /etc/docker` on both Pis, copy to USB. A node someone else can restore from USB without you present is a resilient node.

---

## 9. Total Cost Estimates

| Build Tier | Total Cost | Description |
|---|---|---|
| **Budget** | **~$889** | Single Pi 5, USB SATA storage, external UPS |
| **Recommended** | **~$1,385–$1,425** | Dual Pi 5, NVMe both nodes (GeeekPi dual mount), BC600R UPS inside rack, USB LoRa, custom 1U LoRa panel + LabStack rear fan panel, Anker 747 GaN charger; includes WAN cable, cable labels, U.FL pigtails, M2 standoffs, USB extension, dust filters, black hardware kit |
| **Premium** | **~$1,705–$1,785** | Adds managed switch upgrade (TL-SG108E), USB expansion SSD, cellular modem, Pelican 1610 transport case |
| **Premium + Solar Kit** | **~$2,034–$2,284** | Add solar panel, LiFePO4 battery, charge controller for 24h+ autonomy |
| **Premium + Field Kit** | **~$1,870–$1,960** | Premium build + Pelican case field ops kit (items 36–46); spare cables, recovery USB, backup charger, spare Heltec V3, tools |

### Cost Notes — Feb 2026 Market Conditions
- **⚠️ M.2 2230 NVMe prices are VOLATILE** — Steam Deck/handheld gaming demand has driven up 2230 drive prices significantly; verify before ordering
- **Official Raspberry Pi SSDs: OUT OF STOCK** at PiShop.us as of Feb 2026; use WD SN740 (256GB) and Crucial P310 (1TB) as substitutes
- **Raspberry Pi 5 16GB: $205.00 confirmed** at PiShop.us — up ~40% from mid-2025 due to LPDDR4 shortages
- **GeeekPi RackMate T1 + 2U Touchscreen: SOLD OUT** at DeskPi.com — check Amazon ASINs B0CPLRD29P and B0F3C5R2BZ
- **Tripp Lite BC600R: ~$70 at DigiKey** — verify at Amazon as well; prices vary by retailer
- **Anker 747 GaNPrime 150W GaN charger (~$65):** powers both Pi 5s, GL.iNet, and display from one PDU outlet
- Sales events (Prime Day, Black Friday) can reduce total by 10-15%
- All software is FOSS — zero recurring software licensing costs
- **3D printing savings:** Custom LoRa panel + LabStack rear fan panel (~$4 filament total), rack blank panels, cable guides — saves $20-40

---

## 10. Tools Required for Build

These are not ordered items — they are tools needed during assembly. Verify you have them before build day.

| Tool | Use | Notes |
|---|---|---|
| Precision Phillips screwdriver #0 | NVMe M.2 retention screw on GeeekPi dual mount | The screw is very small — standard screwdrivers won't engage cleanly |
| Anti-static wrist strap or anti-static mat | Handling Pi 5 boards and bare NVMe drives | Pi 5 and NVMe are both susceptible to ESD; ground yourself before touching either |
| MicroSD card reader (USB) | Flashing Raspberry Pi OS onto microSD cards | Most modern laptops have a built-in slot; verify yours does |
| Laptop with browser | GL.iNet setup, switch DOA check, SSH to Pi nodes | Any OS works |
| Flashlight or headlamp | Working inside the rack chassis | The RackMate T1 interior gets dark fast |
| Ruler or calipers | Verify U6 shelf fit (235mm combined vs 236.5mm interior) | Critical before forcing GL.iNet and switch onto the same shelf |

---

## 11. Verify-In-Box Checklist (Before Ordering Extras)

Check these items are actually included with their respective products before purchasing separately:

| Item | Ships With | What to Verify |
|---|---|---|
| NVMe M.2 retention screw × 2 | GeeekPi 1U Dual Pi 5 Mount (B0F7XBVV4D) | Two tiny M.2 screws — one per NVMe slot. If missing, M.2 screw kit (~$3) |
| Touchscreen USB cable (touch input) | GeeekPi 2U Touchscreen (B0F3C5R2BZ) | Usually USB-A to USB-C or USB-A to micro-USB; needed for touch to work |
| Switch 12V DC barrel adapter | TP-Link TL-SG108S | Should be included; verify voltage matches PDU outlet |
| M6 rack mounting screws (silver) | GeeekPi RackMate T1 | T1 includes silver screws — **verify M5 vs M6 by measuring** before ordering black replacements (item 30d). Count included qty; you need ~40 total. |
| Active Cooler mounting hardware | Official Raspberry Pi Active Cooler | Includes push-pins and connector cable |

---

### Price vs. Capability Comparison

Comparable enterprise portable comms kits (Harris PRC-163, Persistent Systems MPU5) cost $10,000–$50,000+. This build delivers encrypted mesh comms, ATAK tactical SA, Monero node, I2P/Tor anonymity, and Tailscale VPN for under $1,500 in commodity hardware.

---

## Appendix A: Quick-Start Checklist

- [ ] Order all components from BOM
- [ ] Assemble rack: rails, shelves, blank panels
- [ ] Flash Raspberry Pi OS to microSD cards
- [ ] Install Pi 5 boards into GeeekPi 1U Dual Pi 5 Mount (B0F7XBVV4D)
- [ ] Insert WD SN740 256GB into Pi #1 NVMe slot (left); Crucial P310 1TB into Pi #2 NVMe slot (right)
- [ ] Enable PCIe Gen 3 on both nodes: add `dtparam=pciex1_gen=3` to /boot/firmware/config.txt
- [ ] Place BC600R UPS at U1, secure with velcro to rack frame
- [ ] Mount PDU at U2, connect 6ft cable down to UPS at U1 (ultra-short run)
- [ ] Mount switch and GL.iNet on shelf at U5
- [ ] Install GeeekPi 1U Dual Pi 5 Mount at U4
- [ ] Install touchscreen at U7-U6
- [ ] Wire all Ethernet (switch to Pi nodes, switch to GL.iNet LAN)
- [ ] Connect HDMI from Pi 5 #1 to touchscreen (2ft cable, U4→U7)
- [ ] Connect Anker 747 GaN charger to PDU outlet 1; connect Pi #1 USB-C to C1, Pi #2 USB-C to C2, GL.iNet USB-C to C3, touchscreen USB-A to USB-A port
- [ ] Connect switch 12V adapter to PDU outlet 2
- [ ] Connect UPS to wall power
- [ ] Power on and verify all components POST
- [ ] Configure GL.iNet: WiFi SSID, DHCP, WireGuard, Tailscale
- [ ] Install services on Pi 5 #1: Conduit Matrix, Tor, I2P, Nginx, Docker
- [ ] Install services on Pi 5 #2: Monero (pre-synced LMDB), OpenTAKServer, Reticulum, Meshtastic
- [ ] Print custom 1U LoRa panel (black PETG); install SMA female bulkhead connectors; mount both Heltec V3 boards on M2 nylon standoffs with OLEDs aligned behind cutout windows (LEFT=RNode, RIGHT=Meshtastic); install in **U8 front rails**
- [ ] Mount 120mm USB exhaust fan on **U8 rear rails** (shares U8 with LoRa panel via open-frame coexistence)
- [ ] Print LabStack 2U Mini 2x 80mm Fan Panel (PETG/PLA+); install in **U4-U3 rear rails** (directly behind Pi mount at U4 front); screw in 2× 80mm USB fans oriented to exhaust rearward
- [ ] Connect U.FL-to-SMA pigtails from each board to its SMA bulkhead on the LoRa panel; mount 915 MHz antennas on bulkhead exterior
- [ ] Connect Heltec V3 LEFT (RNode) to Pi #2 USB 2.0 port 1 via USB-C cable
- [ ] Connect Heltec V3 RIGHT (Meshtastic) to Pi #2 USB 2.0 port 2 via USB-C cable
- [ ] Velcro-mount USB fan hub at U3 interior; plug 5V wall adapter into PDU outlet 3
- [ ] Connect all 3 fan USB cables to USB fan hub (120mm + 2× 80mm) — zero fan cables to Pi ports
- [ ] Set up monitoring dashboards on touchscreen
- [ ] Test remote access via Tailscale
- [ ] Run thermal stress test and verify temperatures
- [ ] Document IP addresses, credentials, recovery procedures

## Appendix B: Key Reference Links

- [Jeff Geerling - Project MINI RACK](https://mini-rack.jeffgeerling.com/)
- [GeeekPi DeskPi RackMate T1](https://deskpi.com/products/deskpi-rackmate-t1-2)
- [GL.iNet Slate AX Documentation](https://www.gl-inet.com/products/gl-axt1800/)
- [Raspberry Pi 5 Documentation](https://www.raspberrypi.com/products/raspberry-pi-5/)
- [Raspberry Pi M.2 HAT+ Documentation](https://www.raspberrypi.com/documentation/accessories/m2-hat-plus.html)
- [Meshtastic Linux-Native Devices](https://meshtastic.org/docs/hardware/devices/linux-native-hardware/)
- [Waveshare SX1262 LoRa HAT Wiki](https://www.waveshare.com/wiki/SX1262_915M_LoRa_HAT)
