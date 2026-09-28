const DEVICE_ID_KEY = "erpnext_mtd_device_id";

function getDeviceId() {
	let deviceId = localStorage.getItem(DEVICE_ID_KEY);

	if (!deviceId) {
		deviceId = crypto.randomUUID();
		localStorage.setItem(DEVICE_ID_KEY, deviceId);
	}

	return deviceId;
}

function getScreen() {
	return {
		width: window.screen.width,
		height: window.screen.height,
		scaling_factor: window.devicePixelRatio,
		color_depth: window.screen.colorDepth,
	};
}

function getTimezone() {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

function getWindowSize() {
    return {
        width: window.innerWidth,
        height: window.innerHeight
    };
}

export async function collectFraudPreventionData() {
	return {
		browser_js_user_agent: navigator.userAgent,
		device_id: getDeviceId(),
		screens: [getScreen()],
		timezone: getTimezone(),
		window_size: getWindowSize(),
	};
}
