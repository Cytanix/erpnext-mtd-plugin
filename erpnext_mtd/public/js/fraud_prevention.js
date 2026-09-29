// ERPNext MTD
//
// Copyright (C) 2026 Cytanix Ltd.
//
// SPDX-License-Identifier: GPL-3.0-only

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
	const offsetMinutes = -new Date().getTimezoneOffset();
	const sign = offsetMinutes >= 0 ? "+" : "-";
	const hours = String(Math.floor(Math.abs(offsetMinutes) / 60)).padStart(2, "0");
	const minutes = String(Math.abs(offsetMinutes) % 60).padStart(2, "0");

	return `UTC${sign}${hours}:${minutes}`;
}

function getWindowSize() {
	return {
		width: window.innerWidth,
		height: window.innerHeight,
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
