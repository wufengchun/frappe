# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import re

import frappe
from frappe import _


@frappe.whitelist()
def get_apps():
	apps = frappe.get_installed_apps()
	app_list = []
	for app in apps:
		if app == "frappe":
			continue
		app_details = frappe.get_hooks("include_as_app", app_name=app)
		if not len(app_details):
			continue
		for app_detail in app_details:
			has_permission_path = app_detail.get("has_permission")
			if has_permission_path and not frappe.get_attr(has_permission_path)():
				continue
			app_list.append(
				{
					"name": app,
					"logo": app_detail.get("logo"),
					"title": _(app_detail.get("title")),
					"route": app_detail.get("route"),
				}
			)
	return app_list


def get_route(app_name):
	hooks = frappe.get_hooks(app_name=app_name)
	if hooks.get("app_icon_route"):
		return hooks.get("app_icon_route")[0]
	return "/apps"


def is_desk_apps(apps):
	for app in apps:
		# check if route is /app or /app/* and not /app1 or /app1/*
		pattern = r"^/app(/.*)?$"
		route = app.get("route")
		if route and not re.match(pattern, route):
			return False
	return True


def get_default_path():
	system_default_app = frappe.get_system_settings("default_app")
	user_default_app = frappe.db.get_value("User", frappe.session.user, "default_app")
	if system_default_app and not user_default_app:
		return get_route(system_default_app)
	elif user_default_app:
		return get_route(user_default_app)

	apps = get_apps()
	_apps = [app for app in apps if app.get("name") != "frappe"]
	if len(_apps) == 1:
		return _apps[0].get("route") or "/apps"
	elif is_desk_apps(_apps):
		return "/app"
	return "/apps"
