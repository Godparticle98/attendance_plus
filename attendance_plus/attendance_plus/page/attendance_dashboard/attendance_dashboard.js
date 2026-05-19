frappe.pages["attendance-dashboard"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Attendance Dashboard",
		single_column: true,
	});

	// Add refresh button
	page.add_primary_action(__("Refresh"), () => load_dashboard(), "octicon octicon-sync");

	// Add filters in toolbar
	let date_field = page.add_field({
		label: "Date",
		fieldtype: "Date",
		fieldname: "date",
		default: frappe.datetime.get_today(),
		change: () => load_dashboard(),
	});

	let dept_field = page.add_field({
		label: "Department",
		fieldtype: "Link",
		fieldname: "department",
		options: "Department",
		change: () => load_dashboard(),
	});

	let status_field = page.add_field({
		label: "Status",
		fieldtype: "Select",
		fieldname: "status",
		options: "\nPresent\nAbsent\nPunch Miss\nLate\nOn Leave",
		change: () => load_dashboard(),
	});

	// Build page HTML
	$(wrapper).find(".layout-main-section").html(`
		<div id="att-dashboard" style="padding: 20px;">

			<!-- Summary Cards -->
			<div id="summary-cards" style="display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:28px;">
				${make_card("cnt-total", "Total", "#2490EF")}
				${make_card("cnt-present", "Present", "#28a745")}
				${make_card("cnt-absent", "Absent", "#dc3545")}
				${make_card("cnt-late", "Late Entry", "#fd7e14")}
				${make_card("cnt-punch-miss", "Punch Miss", "#6f42c1")}
			</div>

			<!-- Attendance Table -->
			<div style="background:var(--card-bg);border-radius:8px;border:1px solid var(--border-color);margin-bottom:28px;">
				<table class="table table-bordered" style="margin:0;">
					<thead style="background:var(--subtle-fg);">
						<tr>
							<th>Employee</th>
							<th>Department</th>
							<th>Check-In</th>
							<th>Check-Out</th>
							<th>Source</th>
							<th>Status</th>
							<th>Action</th>
						</tr>
					</thead>
					<tbody id="att-table-body">
						<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--text-muted);">
							Loading...
						</td></tr>
					</tbody>
				</table>
			</div>

			<!-- Pending Approvals -->
			<h5 style="margin-bottom:14px;">⏳ Pending Approvals</h5>
			<div style="background:var(--card-bg);border-radius:8px;border:1px solid var(--border-color);">
				<table class="table table-bordered" style="margin:0;">
					<thead style="background:var(--subtle-fg);">
						<tr>
							<th>Employee</th>
							<th>Type</th>
							<th>Date</th>
							<th>Request Type</th>
							<th>Reason</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody id="pending-table-body">
						<tr><td colspan="6" style="text-align:center;padding:30px;color:var(--text-muted);">
							Loading...
						</td></tr>
					</tbody>
				</table>
			</div>
		</div>
	`);

	function load_dashboard() {
		let date = date_field.get_value() || frappe.datetime.get_today();
		let dept = dept_field.get_value() || "";
		let status = status_field.get_value() || "";

		// Load attendance data
		frappe.call({
			method: "attendance_plus.api.dashboard.get_attendance_data",
			args: { date: date, department: dept, status_filter: status },
			callback: function (r) {
				if (r.message) {
					update_summary(r.message.summary);
					render_attendance_table(r.message.rows);
				}
			},
		});

		// Load pending approvals
		frappe.call({
			method: "attendance_plus.api.dashboard.get_pending_approvals",
			callback: function (r) {
				render_pending_table(r.message || []);
			},
		});
	}

	function update_summary(s) {
		$("#cnt-total .count").text(s.total || 0);
		$("#cnt-present .count").text(s.present || 0);
		$("#cnt-absent .count").text(s.absent || 0);
		$("#cnt-late .count").text(s.late || 0);
		$("#cnt-punch-miss .count").text(s.punch_miss || 0);
	}

	function render_attendance_table(rows) {
		let tbody = $("#att-table-body");
		if (!rows || !rows.length) {
			tbody.html(`<tr><td colspan="7" style="text-align:center;padding:30px;color:var(--text-muted);">No records found</td></tr>`);
			return;
		}
		tbody.html(rows.map((row) => `
			<tr>
				<td><b>${row.employee_name}</b><br>
					<small style="color:var(--text-muted)">${row.employee}</small>
				</td>
				<td>${row.department || "-"}</td>
				<td>${row.in_time || '<span style="color:#dc3545">Missing</span>'}</td>
				<td>${row.out_time || '<span style="color:#dc3545">Missing</span>'}</td>
				<td><small style="color:var(--text-muted)">${row.source || "-"}</small></td>
				<td>${badge_for(row.status)}</td>
				<td>${
					["Punch Miss", "Absent"].includes(row.status)
						? `<a href="/app/attendance-regularization/new-attendance-regularization-1?employee=${row.employee}&date=${row.date}" 
							style="font-size:12px;">+ Regularize</a>`
						: "-"
				}</td>
			</tr>
		`).join(""));
	}

	function render_pending_table(rows) {
		let tbody = $("#pending-table-body");
		if (!rows.length) {
			tbody.html(`<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-muted);">No pending approvals</td></tr>`);
			return;
		}
		tbody.html(rows.map((row) => `
			<tr>
				<td><b>${row.employee_name}</b></td>
				<td>${row.doctype_label}</td>
				<td>${row.date}</td>
				<td>${row.request_type}</td>
				<td>${row.reason || "-"}</td>
				<td>
					<button class="btn btn-xs btn-success" style="margin-right:4px;"
						onclick="handle_approval('${row.doctype}', '${row.name}', 'approve')">
						Approve
					</button>
					<button class="btn btn-xs btn-danger"
						onclick="handle_approval('${row.doctype}', '${row.name}', 'reject')">
						Reject
					</button>
				</td>
			</tr>
		`).join(""));
	}

	window.handle_approval = function (doctype, name, action) {
		frappe.prompt(
			{ label: "Remarks (optional)", fieldtype: "Small Text", fieldname: "remarks" },
			(values) => {
				let method_map = {
					"Attendance Permission": {
						approve: "attendance_plus.doctype.attendance_permission.attendance_permission.approve_permission",
						reject: "attendance_plus.doctype.attendance_permission.attendance_permission.reject_permission",
					},
					"Attendance Regularization": {
						approve: "attendance_plus.doctype.attendance_regularization.attendance_regularization.approve_regularization",
						reject: "attendance_plus.doctype.attendance_regularization.attendance_regularization.reject_regularization",
					},
				};
				frappe.call({
					method: method_map[doctype][action],
					args: { doc_name: name, remarks: values.remarks || "" },
					callback: () => {
						frappe.show_alert({
							message: `${frappe.utils.titleCase(action)}d successfully`,
							indicator: action === "approve" ? "green" : "red",
						});
						load_dashboard();
					},
				});
			},
			__("Confirm " + frappe.utils.titleCase(action)),
			__(frappe.utils.titleCase(action))
		);
	};

	function badge_for(status) {
		let map = {
			Present: "success",
			Absent: "danger",
			Late: "warning",
			"Punch Miss": "primary",
			"Half Day": "info",
			"On Leave": "secondary",
		};
		let cls = map[status] || "secondary";
		return `<span class="badge badge-${cls}">${status || "Unknown"}</span>`;
	}

	function make_card(id, label, color) {
		return `
			<div id="${id}" style="background:var(--card-bg);border-radius:10px;
				padding:20px;text-align:center;border:1px solid var(--border-color);">
				<div class="count" style="font-size:32px;font-weight:700;color:${color};">-</div>
				<div style="font-size:12px;color:var(--text-muted);margin-top:4px;">${label}</div>
			</div>`;
	}

	// Initial load
	load_dashboard();

	// Auto-refresh every 2 minutes
	setInterval(load_dashboard, 120000);
};
