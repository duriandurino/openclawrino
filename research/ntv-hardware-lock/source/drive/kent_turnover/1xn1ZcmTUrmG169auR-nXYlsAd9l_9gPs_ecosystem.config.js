module.exports = {
	apps: [
		{
			name: "player-server",
			cwd: "/home/pi/n-compasstv/player-server/",
			script: "./src/app.js",
			max_memory_restart: '500M'
		},
		{
			name: "player-puppeteer",
			cwd: "/home/pi/n-compasstv/player-puppeteer/",
			script: "./app.js",
			max_memory_restart: '300M'
		},
		{
			name: "player-electron",
			cwd: "/home/pi/n-compasstv/player-electron/",
			script: "npm",
			args: "start",
			max_memory_restart: '300M'
		},
		{
			name: "player-chromium",
			cwd: "/home/pi/n-compasstv/player-server/src/bin/",
			script: "./chromium-browser-kiosk-mode.sh",
			max_memory_restart: '300M'
		}
	]
} 