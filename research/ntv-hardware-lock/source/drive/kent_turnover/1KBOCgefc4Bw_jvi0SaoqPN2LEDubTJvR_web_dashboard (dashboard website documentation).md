# NCompass TV Dashboard

Web-based management platform for the NTV360 digital signage network. Dealers and admins use this dashboard to manage venues, content, playlists, and player devices — all of which are connected to the NTV360 Pi players in the field.

> **URL:** [dev-dashboard.n-compass.online](https://dev-dashboard.n-compass.online/login) (Development)
> **Production:** `dashboard.n-compass.online`

---

## Table of Contents

- [How the Dashboard and Player Connect](#how-the-dashboard-and-player-connect)
- [User Roles](#user-roles)
- [Admin View](#admin-view)
  - [Dashboard (Admin)](#dashboard-admin)
  - [Dealers](#dealers)
  - [Hosts](#hosts)
  - [Licenses](#licenses)
  - [Single License Page (Player Control)](#single-license-page-player-control)
  - [Advertisers](#advertisers)
  - [Locator](#locator)
  - [Tags](#tags)
  - [Media Library](#media-library)
  - [Feeds](#feeds)
  - [Fillers Library](#fillers-library)
  - [Playlists](#playlists)
  - [Screens](#screens)
  - [Installations](#installations)
  - [Users](#users)
  - [Templates](#templates)
  - [Directory](#directory)
  - [Reports](#reports)
- [Dealer View](#dealer-view)
  - [Dashboard (Dealer)](#dashboard-dealer)
  - [Dealer-Scoped Sections](#dealer-scoped-sections)
- [Content Workflow: Dashboard → Player](#content-workflow-dashboard--player)
- [Platform Statistics](#platform-statistics)

---

## How the Dashboard and Player Connect

The dashboard is the **control plane** for every NTV360 Raspberry Pi player in the field. Here is the end-to-end flow:

```
┌─────────────────────────────────────────────────────────┐
│             N-Compass TV Dashboard (Web)                │
│                                                         │
│  Admin/Dealer creates & configures:                     │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐             │
│  │  Content │→ │ Playlists │→ │ Screens  │             │
│  │(Media    │  │(Scheduling│  │(Zones/   │             │
│  │ Library) │  │ & Order)  │  │Templates)│             │
│  └──────────┘  └───────────┘  └──────────┘             │
│                                     │                  │
│                           Assigned to License          │
│                                     │                  │
│  ┌──────────────────────────────────▼──────────────┐   │
│  │               License Management                │   │
│  │  Generate License Key → Assign to Host          │   │
│  │  Remote Controls: Reboot, Content Update, etc.  │   │
│  └─────────────────────┬────────────────────────── ┘   │
└────────────────────────┼────────────────────────────────┘
                         │
              WebSocket + REST API
              (nctvapi2 / nctvsocket)
                         │
┌────────────────────────▼────────────────────────────────┐
│                  NTV360 Pi Player                        │
│                                                         │
│  1. Enter License Key → binds player to a Host          │
│  2. Player pulls playlists, content, and schedules      │
│  3. Downloads media assets locally                      │
│  4. Chromium kiosk displays content                     │
│  5. Player sends play logs, screenshots, telemetry      │
│  6. Receives socket commands from the dashboard         │
└─────────────────────────────────────────────────────────┘
```

### The License Key is the Bridge

The license key generated in the dashboard is what links a specific Pi player to a specific host/venue in the platform. When a player is configured with a license key:

1. The player registers itself with the NCompass TV API
2. The cloud knows the player is active (`Online` status)
3. Content assigned to that license flows down to the player
4. The dashboard gains the ability to send real-time commands to that player

---

## User Roles

| Role | Access Level | Description |
|---|---|---|
| **Admin** | Full platform access | Manages all dealers, hosts, licenses, users, templates across the entire network |
| **Dealer** | Scoped to own accounts | Manages their own hosts, licenses, and content; cannot see other dealers' data |

---

## Admin View

Admins have access to every section of the platform. The admin account is typically the NCompass TV company-level account.

### Dashboard (Admin)

**URL:** `/administrator/dashboard`

The admin dashboard provides a high-level overview of the entire platform:

| Metric | Description |
|---|---|
| **Dealers** | Total, active, and inactive dealer accounts |
| **Hosts** | Total, active, and inactive host (venue) locations |
| **Advertisers** | Total, active, and inactive advertiser profiles |
| **Licenses** | Assigned vs. unassigned licenses across the platform |
| **Average per Dealer** | Average number of hosts, advertisers, and licenses per dealer |
| **Today's Activities** | Content uploads and feeds created today |
| **Scheduled Installation Stats** | Upcoming, current, and past-month installation counts |
| **Users Today** | Number of user sign-ins today |

---

### Dealers

**URL:** `/administrator/dealers`

Dealers are the franchisee-level businesses that operate under the NCompass TV umbrella. Each dealer manages their own set of hosts, advertisers, and licenses.

| Feature | Description |
|---|---|
| Add/Edit Dealer | Create or update dealer accounts |
| Dealer Alias | Short identifier used in license naming (e.g., `501-ACO`) |
| Active/Inactive status | Toggle dealer account visibility |
| Dealer stats | View their hosts, licenses, and advertiser counts |

---

### Hosts

**URL:** `/administrator/hosts`

A **Host** is a physical venue or business location where a player is installed (e.g., a restaurant, gym, medical office).

| Feature | Description |
|---|---|
| Add Host Place | Register a new physical location |
| Add Host User | Add a user account for a host business |
| Host status | Active / Inactive |
| Views | Hosts View, Dealers View, DMA View, Placer Data |
| Host data | Business name, timezone, operation hours, venue ID |

Each host can have multiple licenses (multiple player screens at the same location). The host's timezone and business hours determine when the player's TV display turns on and off via HDMI-CEC.

---

### Licenses

**URL:** `/administrator/licenses`

Licenses are the **core entity** that link the dashboard to a physical Pi player. Each license represents one player screen installation.

#### Generating a License

1. Click **Generate License** on the Licenses page
2. Select the license type (Ad screen, Menu board, etc.)
3. Optionally assign it to a dealer and host immediately
4. A unique UUID license key is created (e.g., `03125c6d-69b1-4780-b7fa-48b8fea40ab3`)

#### License List Views and Filters

| Filter/View | Description |
|---|---|
| **License Status** | Filter by Online, Offline, Pending, Inactive |
| **Timezone** | Filter by the host's timezone |
| **User** | Filter by assigned user |
| **Player** | Filter by player type |
| **Order by License Status** | Sort licenses by connectivity status |
| **Outdated tab** | Licenses running outdated player software |
| **Dealers View** | Group licenses by dealer |
| **Tags View** | Group licenses by assigned tags |
| **Hosts View** | Group licenses by host/venue |
| **Advertisers View** | Group licenses by advertiser |
| **List / Grid View** | Toggle between table and card layout |
| **Export** | Export license data to CSV |
| **Show/Hide Columns** | Customize visible table columns |

#### License Status Colors

| Status | Meaning |
|---|---|
| Green dot | **Online** -- Player is connected and communicating |
| Red dot | **Offline** -- Player is not responding |
| Orange/Yellow dot | **Pending** -- Player is registered but not yet confirmed |
| Grey | **Inactive** -- License is deactivated |

#### Tags on Licenses

Tags (e.g., `InsigniaFire`, `ONN_Roku`, `55" TV`, `No_CEC`) are color-coded labels attached to licenses for quick identification of the player hardware type or specific configuration notes.

---

### Single License Page (Player Control)

**URL:** `/administrator/licenses/<license-uuid>`

This is the most important page for managing an individual player. It provides real-time remote control of the Pi device.

#### Remote Control Buttons

| Button | Action on Pi Player |
|---|---|
| **Check Status** | Pings the player and retrieves its current state (connection, last seen, etc.) |
| **Content Update** | Sends a socket command to trigger an immediate content sync from the cloud |
| **Refetch Content** | Forces the player to re-download all content assets from scratch |
| **Reboot Player (Software)** | Restarts the `player-server` and Chromium processes via PM2 (does not reboot the OS) |
| **Reboot Pi (Device)** | Sends a full `sudo reboot` command to the Raspberry Pi |
| **Reset Data** | Wipes the player's local SQLite database and content cache; requires re-entering license key |
| **2.0 Upgrade** | Upgrades the player software to the latest v2 release |
| **Delete License** | Permanently removes the license from the platform |

> **Player-side mechanism:** All these buttons communicate through the Socket.IO connection between the dashboard and the `player-server` process on the Pi. The buttons are disabled (grayed out) when the player is Offline because the socket connection is not active.

#### License Detail Tabs

| Tab | Content |
|---|---|
| **Details** | Host info, timezone, business hours, display settings, AnyDesk ID, last seen timestamps, CEC settings, screenshot |
| **Content** | Currently assigned playlist, content items, play schedule |
| **Terminal** | Live terminal / command output from the player (admin only) |
| **Activity** | Audit log of all actions taken on this license |
| **Installation** | Installation request history, technician notes, scheduled install dates |

---

### Advertisers

**URL:** `/administrator/advertisers`

Advertisers are businesses or brands whose content is played across the network. They are separate from the host venues (a host plays a mix of their own content and advertiser content).

| Feature | Description |
|---|---|
| Add Advertiser Profile | Create an advertiser business profile |
| Add Advertiser User | Create a login for an advertiser to upload their own content |
| Region/State/Status filters | Narrow the advertiser list |
| Content management | Advertisers can upload content to their profile which dealers assign to playlists |

---

### Locator

**URL:** `/administrator/locator`

An interactive map showing the geographic distribution of all host locations. Useful for visualizing network coverage.

---

### Tags

**URL:** `/administrator/tags`

Tags are custom labels attached to licenses for filtering and identification. Examples seen in the platform:

- Hardware identifiers: `InsigniaFire`, `ONN_Roku`, `HisenseRoku`, `55" TV`
- Configuration notes: `No_CEC`, `Plug`
- Custom labels for grouping or support tracking

---

### Media Library

**URL:** `/administrator/media-library`

Central repository for all uploaded media content across the platform.

| Metric | Value (as of Mar 2026) |
|---|---|
| Total Contents | 89,920 |
| Videos | 38,892 |
| Images | 48,828 |
| Feeds | 2,190 |

| Feature | Description |
|---|---|
| **Upload Media** | Upload images or video files for use in playlists |
| **Delete** | Remove selected media items |
| **Reassign** | Move media from one dealer/host to another |
| Toggle switch | Filter between media types |

Content uploaded here is downloaded by the player to `/var/www/html/assets/` on the Pi when assigned to a playlist that the license subscribes to.

---

### Feeds

**URL:** `/administrator/feeds`

Feeds are dynamic, data-driven content sources (e.g., news tickers, weather, RSS feeds, social media walls) that can be added to playlists as live content zones alongside static media.

---

### Fillers Library

**URL:** `/administrator/fillers`

Filler content is shown in playlist zones when no scheduled content is available for a particular time slot. Fillers ensure the screen is never blank. Each filler has a position in a rotation queue and plays in order when triggered.

---

### Playlists

**URL:** `/administrator/playlists`

Playlists define the sequence and scheduling of content items to be played on a screen.

| Metric | Value |
|---|---|
| Total Playlists | 4,521 |
| Active | 3,301 |
| Inactive | 1,220 |

| Feature | Description |
|---|---|
| **Create Playlist** | Build a new playlist for a dealer/host |
| Content items | Add videos, images, feeds, or fillers to the playlist |
| **Scheduling** | Each item can have: date range, specific days of week, start/end time, alternate-week patterns |
| **Duration** | Set how long each item plays |
| **Is Fullscreen** | Override the template zone and play content fullscreen |
| Sequence | Drag to reorder items in the playlist |

On the player side, the playlist is stored in the `playlist_contents` SQLite table and drives what Chromium displays and when.

---

### Screens

**URL:** `/administrator/screens`

Screens define the display configuration assigned to a license. Each screen has a template zone layout that determines how content is arranged on the TV.

| Metric | Value |
|---|---|
| Total Screens | 5,553 |

| Feature | Description |
|---|---|
| **New Screen** | Create a new screen configuration |
| Template assignment | Select which template layout the screen uses |
| Zone assignment | Assign a playlist to each zone in the template |
| Screen name | Identify the screen (e.g., "Front Lobby", "Bar Area") |

---

### Installations

**URL:** `/administrator/installations`

Tracks scheduled and completed player installation jobs. Used by the field technician team to manage the physical deployment of Pi players to host locations.

| Feature | Description |
|---|---|
| Scheduled installs | View upcoming installation appointments |
| Status tracking | Pending, In Progress, Completed |
| Welcome modal | Shows today's, tomorrow's, and next 3 days' installation counts on login |

---

### Users

**URL:** `/administrator/users`

Manages all user accounts across the platform (admin, dealer, host, and advertiser users).

---

### Templates

**URL:** `/administrator/templates`

Templates define the **visual zone layout** of a screen. Each template divides the display into named zones, and each zone gets its own playlist.

Example templates visible in the platform:

| Template | Zones |
|---|---|
| **NCT Standard Template** | Main (large left area), Vertical (right strip), Horizontal (bottom bar) |
| Custom templates | Up to 4+ zones (Upper Left, Lower Left, Main, etc.) |

Templates are stored in the `template_zones` table on the player. The player-server uses this data to instruct the Chromium frontend on how to position and size each content zone on the screen.

---

### Directory

**URL:** `/administrator/directory`

A structured directory of dealers, hosts, and advertiser organizations, likely used for organizational navigation or reporting.

---

### Reports

**URL:** `/administrator/reports`

Analytics and reporting section with multiple sub-tabs:

| Tab | Description |
|---|---|
| **Hosts** | Host growth chart (total hosts per year), US map with state-level breakdowns, top dealers by host count |
| **Content** | Content upload trends, most-played content |
| **Licenses** | License activation trends, online/offline rates |
| **Installations** | Installation completion rates over time |

Reports support date range filtering and per-dealer breakdowns.

---

## Dealer View

Dealers have a focused interface showing only their own data.

### Dashboard (Dealer)

**URL:** `/dealer/dashboard`

| Feature | Description |
|---|---|
| Welcome message | Personalized greeting with platform-wide stats ("33 states, 90 markets, 1,700+ locations") |
| License Status widget | Count of Online, Offline, and Pending licenses for this dealer |

### Dealer-Scoped Sections

Dealers have access to a subset of the admin sections, scoped to only their accounts:

| Section | Available | Notes |
|---|---|---|
| Dashboard | Yes | Shows only their license status |
| Hosts | Yes | Only their own host locations |
| Licenses | Yes | Only their own licenses; shows per-license Online/Offline/Pending status with type breakdown (Ad, Menu, Unassigned) |
| Advertisers | Yes | Only their own advertiser profiles |
| Locator | Yes | Map view of their host locations |
| Tags | Yes | Their own tags |
| Media Library | Yes | Their own uploaded content |
| Feeds | Yes | Their own feeds |
| Fillers Library | Yes | Their own filler content |
| Playlists | Yes | Their own playlists |
| Screens | Yes | Their own screen configurations |
| Reports | Yes | Their own host/content/license analytics |
| **Dealers** | No | Admin-only |
| **Users** | No | Admin-only |
| **Templates** | No | Admin-only (dealers use existing templates) |
| **Directory** | No | Admin-only |
| **Installations** | No | Admin-only |

---

## Content Workflow: Dashboard → Player

This is the complete flow of how content configured in the dashboard ends up playing on a Pi screen:

```
1. UPLOAD CONTENT
   Media Library → Upload images/videos/feeds

2. CREATE PLAYLIST
   Playlists → Create Playlist → Add content items
   → Set each item's duration, schedule, and days

3. DESIGN SCREEN LAYOUT
   Templates → Choose zone layout (Main, Vertical, Horizontal, etc.)
   Screens → New Screen → Assign template + assign playlist to each zone

4. ASSIGN TO LICENSE
   Licenses → Open a license → Assign host → Assign screen

5. PLAYER RECEIVES CONTENT
   Player (Pi) polls the NCompass TV API
   → Downloads playlist metadata
   → Downloads media files to /var/www/html/assets/
   → Stores schedule in local SQLite DB

6. CHROMIUM PLAYS CONTENT
   player-server reads playlist + template from DB
   → Chromium (kiosk) renders the UI with zones
   → Content plays according to schedule

7. REPORTING
   Player records play logs → Sends to cloud API
   Dashboard Reports section shows playback data
```

---

## Platform Statistics

Snapshot of the production-like development environment (as of March 2026):

| Entity | Count |
|---|---|
| Dealers | 416 (272 active) |
| Hosts | 5,393 (5,309 active) |
| Advertisers | 4,893 (4,780 active) |
| Licenses | 6,058 total (5,215 assigned) |
| Screens | 5,553 |
| Playlists | 4,521 (3,301 active) |
| Media Files | 89,920 (38,892 videos + 48,828 images + 2,190 feeds) |

---

## Connection Reference: Dashboard ↔ Player

| Dashboard Action | What Happens on the Pi |
|---|---|
| Generate License Key | Creates a key; player must be configured with it manually |
| Assign screen/playlist to license | Player fetches new playlist on next content sync |
| **Content Update** button | `player-server` receives socket event, calls content sync API |
| **Refetch Content** button | Player deletes local assets and re-downloads everything |
| **Reboot Player** button | `pm2 restart player-server player-chromium` |
| **Reboot Pi** button | `sudo reboot` executed on the Pi |
| **Reset Data** button | `curl http://localhost:3215/api/content/reset` |
| **Check Status** button | Dashboard queries last-seen timestamp and socket status |
| Screenshot (socket event) | `scrot` captures screen → uploaded to S3 → shown in Details tab |
| Speedtest (socket event) | `speedtest-cli` runs → results saved to `internet_logs` table |
| CEC Control (socket event) | `cec-client` sends power on/off command to TV |
| AnyDesk Reset (socket event) | `sudo rm /etc/anydesk/service.conf` + restart anydesk service |
| Business hours set on host | Player CEC cron checks hours → powers TV on/off accordingly |

---

*Last updated: March 2026*
