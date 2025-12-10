
import { registry } from '@web/core/registry';
const { Component, onWillStart, onMounted, useState, useRef } = owl
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { loadJS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";

export class garageAnalysisDashboard extends Component {
  setup() {
    this.action = useService("action");
    this.orm = useService("orm");
    this.rpc = this.env.services.rpc
    this.state = useState({

      user_name: { value: 'User Image' },
      user_img: { value: 'User Name' },
      total_won_lead_ids: [],
      total_lead_ids: [],
      total_rfq_ids: [],
      total_work_order_list: [],
      total_sale_list: [],
      total_invoice_list: [],
      total_due_invoice_list: [],
      total_request: [],
      draft_job_card_list: [],
      confirm_job_card_list: [],
      in_process_job_card_list: [],
      total_diagnosis_list: [],
      total_rfq_list: [],
      total_sales_list: [],
      garage_lead_list: [],
      garage_lead_list: {},
      rowsPerPage: 10,
      garage_lead_list_length: 0,
      current_garage_lead_page: 1,

      garage_due_invoice_list: [],
      garage_due_invoice_list: {},
      garage_due_invoice_list_length: 0,
      current_garage_due_invoice_page: 1,

      garage_paid_invoice_list: [],
      garage_paid_invoice_list: {},
      garage_paid_invoice_list_length: 0,
      current_garage_paid_invoice_page: 1,
    })
    onMounted(this.onMounted);
    onWillStart(this.onWillStart)

  }

  async onWillStart() {
    await this.getCardData()
    await this.getGreetings()
    await loadJS("https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js")
  }

  async getGreetings() {
    var self = this;
    const now = new Date();
    const hours = now.getHours();
    if (hours >= 5 && hours < 12) {
      self.greetings = "Good Morning";
    }
    else if (hours >= 12 && hours < 18) {
      self.greetings = "Good Afternoon";
    }
    else {
      self.greetings = "Good Evening";
    }
  }

  async onMounted() {
    this._onchangeJobCardByTeamChart();
    this._onchangeJobCardByStateChart();
    this._onchangeDueInvoiceChart();
    this._onchangeTopSellingProductChart();
    this._onchangeTopCustomerRevenueChart();
    this._onchangeTopRepeatedCustChart();
    this.render_garage_lead_list(this.state.rowsPerPage, this.state.current_garage_lead_page);
    this.render_garage_due_invoice_list(this.state.rowsPerPage, this.state.current_garage_due_invoice_page);
    this.render_garage_paid_invoice_list(this.state.rowsPerPage, this.state.current_garage_paid_invoice_page);
    this.render_garage_filter();
  }

  _onchangeGrageFilter(ev) {
    this.flag = 1
    var user_selection = document.querySelector('#user_selection').value;
    var customer_selection = document.querySelector('#customer_selection').value;
    var duration_selection = document.querySelector('#request_date').value;
    this._onchangeJobCardByTeamChart();
    this._onchangeJobCardByStateChart();
    this._onchangeDueInvoiceChart();
    this._onchangeTopSellingProductChart();
    this._onchangeTopCustomerRevenueChart();
    this._onchangeTopRepeatedCustChart();
    this.render_garage_lead_list(this.state.rowsPerPage, this.state.current_garage_lead_page);
    this.render_garage_due_invoice_list(this.state.rowsPerPage, this.state.current_garage_due_invoice_page);
    this.render_garage_paid_invoice_list(this.state.rowsPerPage, this.state.current_garage_paid_invoice_page);


    var self = this;
    rpc('/garage/filter-apply', {
      'data': {
        'user': user_selection,
        'customer': customer_selection,
        'duration': duration_selection,

      }
    }).then(function (data) {
      self.state.total_won_lead_ids = data['total_won_lead']
      self.state.total_lead = data['total_lead']
      self.state.total_work_order_list = data['total_work_order']
      self.state.total_due_invoice_list = data['due_invoice_list'],
      self.state.total_invoice_list = data['paid_invoice_list'],
      self.state.total_request = data['total_request'],
      self.state.draft_job_card_list = data['draft_job_card'],
      self.state.confirm_job_card_list = data['confirm_job_card'],
      self.state.in_process_job_card_list = data['in_process_job_card'],
      self.state.total_diagnosis_list = data['total_diagnosis'],
      self.state.total_rfq_list = data['total_rfq'],
      self.state.total_sales_list = data['total_sales_ids']
    })
  }

  _downloadChart(e) {
    var chartId = e.target.id.slice(0, e.target.id.length - 4)
    var chartEle = document.querySelector("#" + chartId)
    const imageDataURL = chartEle.toDataURL('image/png'); // Generate image data URL
    const filename = chartId + '.png'; // Set your preferred filename
    const link = document.createElement('a');
    link.href = imageDataURL;
    link.download = filename;
    link.click();
  }

  downloadReport(e) {
    window.print();

  }

  // Job card by team
  async _onchangeJobCardByTeamChart(ev) {
    var user_selection = document.querySelector('#user_selection').value;
    var customer_selection = document.querySelector('#customer_selection').value;
    var duration_selection = document.querySelector('#request_date').value;
    var team_wise_job_card_type = document.querySelector('#job_card_team_chart_selection').value;
    var self = this;
    await rpc("/garage/job_card/chart/data",
      {
        'data':
        {
          'user_id': user_selection,
          'customer_id': customer_selection,
          'duration': duration_selection,
        }
      }).then(function (data) {
        var ctx = document.querySelector("#job_card_by_team_chart_data");
        new Chart(ctx, {
          type: team_wise_job_card_type,
          data: data.team_wise_job_card_chart_data,
          options: {
            maintainAspectRatio: false,
            onClick: (evt, elements) => {
              if (elements.length > 0) {
                const element = elements[0];
                const clickedIndex = element.index;
                const clickedLabel = data.team_wise_job_card_chart_data.labels[clickedIndex];
                const clickedValue = data.team_wise_job_card_chart_data.datasets[0].detail[clickedIndex]

                var options = {
                };
                self.action.doAction({
                  name: _t(clickedLabel),
                  type: 'ir.actions.act_window',
                  res_model: 'dev.repair.request',
                  domain: [["id", "in", clickedValue]],
                  view_mode: 'list,form',
                  views: [
                    [false, 'list'],
                    [false, 'form']
                  ],
                  target: 'current'
                }, options)
              } else {

              }
            }
          }
        });
      });
  }

  // Job card by state
  async _onchangeJobCardByStateChart(ev) {
    var user_selection = document.querySelector('#user_selection').value;
    var customer_selection = document.querySelector('#customer_selection').value;
    var duration_selection = document.querySelector('#request_date').value;
    var sate_wise_job_card_type = document.querySelector('#job_card_by_state_chart_selection').value;


    var self = this;
    await rpc("/garage/job_card/state/chart/data",
      {
        'data':
        {
          'user_id': user_selection,
          'customer_id': customer_selection,
          'duration': duration_selection,

        }
      }).then(function (data) {
        var ctx = document.querySelector("#job_card_by_state_chart_data");
        new Chart(ctx, {
          type: sate_wise_job_card_type,
          data: data.state_wise_job_card_chart_data,
          options: {
            maintainAspectRatio: false,
            onClick: (evt, elements) => {
              if (elements.length > 0) {
                const element = elements[0];
                const clickedIndex = element.index;
                const clickedLabel = data.state_wise_job_card_chart_data.labels[clickedIndex];
                const clickedValue = data.state_wise_job_card_chart_data.datasets[0].detail[clickedIndex]

                var options = {
                };
                self.action.doAction({
                  name: _t(clickedLabel),
                  type: 'ir.actions.act_window',
                  res_model: 'dev.repair.request',
                  domain: [["id", "in", clickedValue]],
                  view_mode: 'list,form',
                  views: [
                    [false, 'list'],
                    [false, 'form']
                  ],
                  target: 'current'
                }, options)
              } else {

              }
            }
          }
        });
      });
  }


  //customer  due invoice chart

  async _onchangeDueInvoiceChart(ev) {
    var user_selection = document.querySelector('#user_selection').value;
    var customer_selection = document.querySelector('#customer_selection').value;
    var duration_selection = document.querySelector('#request_date').value;
    var due_invoice_chart_selection = document.querySelector('#due_invoice_chart_selection').value;
    var top_due_invoice_select = document.querySelector('#top_due_invoice_select').value;
    var self = this;
    await rpc("/customer/due/invoice/chart/data",
      {
        'data':
        {
          'user_id': user_selection,
          'partner_id': customer_selection,
          'duration':duration_selection,
          'top_due_invoice_select': top_due_invoice_select,
        }
      }).then(function (data) {
        var ctx = document.querySelector("#due_invoice_chart_data");
        new Chart(ctx, {
          type: due_invoice_chart_selection,
          data: data.due_invoice_chart_data,
          options: {
            maintainAspectRatio: false,
            onClick: (evt, elements) => {
              if (elements.length > 0) {
                const element = elements[0];
                const clickedIndex = element.index;
                const clickedLabel = data.due_invoice_chart_data.labels[clickedIndex];
                const clickedValue = data.due_invoice_chart_data.datasets[0].detail[clickedIndex]
                console.log("Clicked label:", clickedLabel, "Clicked value:", clickedValue);
                var options = {
                };
                self.action.doAction({
                  name: _t(clickedLabel),
                  type: 'ir.actions.act_window',
                  res_model: 'account.move',
                  domain: [["id", "in", clickedValue]],
                  view_mode: 'list,form',
                  views: [
                    [false, 'list'],
                    [false, 'form']
                  ],
                  target: 'current'
                }, options)
              } else {
                console.log("Click outside chart area");
              }
            }
          }
        });
      });
  }

  // Top Product Selling chart

  async _onchangeTopSellingProductChart(ev) {
    var user_selection = document.querySelector('#user_selection').value;
    var customer_selection = document.querySelector('#customer_selection').value;
    var duration_selection = document.querySelector('#request_date').value;
    var product_chart_selection = document.querySelector('#product_chart_selection').value;
    var top_product_selling_count = document.querySelector('#top_product_selling_count').value;
    var self = this;
    await rpc("/top/product/selling/chart/data",
      {
        'data':
        {
          'user_id': user_selection,
          'partner_id': customer_selection,
          'duration':duration_selection,
          'top_product_selling_count': top_product_selling_count,
        }
      }).then(function (data) {
        var ctx = document.querySelector("#top_selling_product_chart_data");
        new Chart(ctx, {
          type: product_chart_selection,
          data: data.top_selling_product_chart_data,
          options: {
            maintainAspectRatio: false,

            onClick: (evt, elements) => {
              if (elements.length > 0) {
                const element = elements[0];
                const clickedIndex = element.index;
                const clickedLabel = data.top_selling_product_chart_data.labels[clickedIndex];
                const clickedValue = data.top_selling_product_chart_data.datasets[0].detail[clickedIndex]
                var options = {
                };
                self.action.doAction({
                  name: _t(clickedLabel),
                  type: 'ir.actions.act_window',
                  res_model: 'sale.order.line',
                  domain: [["id", "in", clickedValue]],
                  view_mode: 'list,form',
                  views: [
                    [false, 'list'],
                    [false, 'form']
                  ],
                  target: 'current'
                }, options)
              } else {
              }
            }
          }
        });
      });
  }


// Top customer by revenue
  async _onchangeTopCustomerRevenueChart(ev) {
    var user_selection = document.querySelector('#user_selection').value;
    var customer_selection = document.querySelector('#customer_selection').value;
    var duration_selection = document.querySelector('#request_date').value;
    var top_cust_rev_chart_selection = document.querySelector('#top_cust_rev_chart_selection').value;
    var top_cust_rev_range_selection = document.querySelector('#top_cust_rev_range_selection').value;
    var self = this;
    await rpc("/top/customer/revenue/chart/data",
      {
        'data':
        {
          'user_id': user_selection,
          'partner_id': customer_selection,
          'duration':duration_selection,
          'top_cust_revenue_count': top_cust_rev_range_selection,
        }
      }).then(function (data) {
    console.log("===============================dd============")

        var ctx = document.querySelector("#top_customer_revenue_chart_data");
        new Chart(ctx, {
          type: top_cust_rev_chart_selection,
          data: data.top_cust_revenue_chart_data,
          options: {
            maintainAspectRatio: false,

            onClick: (evt, elements) => {
              if (elements.length > 0) {
                const element = elements[0];
                const clickedIndex = element.index;
                const clickedLabel = data.top_cust_revenue_chart_data.labels[clickedIndex];
                const clickedValue = data.top_cust_revenue_chart_data.datasets[0].detail[clickedIndex]
                var options = {
                };
                self.action.doAction({
                  name: _t(clickedLabel),
                  type: 'ir.actions.act_window',
                  res_model: 'sale.order',
                  domain: [["id", "in", clickedValue]],
                  view_mode: 'list,form',
                  views: [
                    [false, 'list'],
                    [false, 'form']
                  ],
                  target: 'current'
                }, options)
              } else {
              }
            }
          }
        });
      });
  }

  // Top Repeated customer


  async _onchangeTopRepeatedCustChart(ev) {
     var user_selection = document.querySelector('#user_selection').value;
    var customer_selection = document.querySelector('#customer_selection').value;
    var duration_selection = document.querySelector('#request_date').value;
    var customer_chart_selection = document.querySelector('#customer_chart_selection').value;
    var top_team_order_count = document.querySelector('#top_team_order_count').value;
    var self = this;
    await rpc("/top/repeated/cust/chart/data",
      {
        'data':
        {
          'user_id': user_selection,
          'partner_id': customer_selection,
          'duration':duration_selection,
          'top_team_order_count': top_team_order_count,
        }
      }).then(function (data) {
        var ctx = document.querySelector("#top_repeated_customer_chart_data");
        new Chart(ctx, {
          type: customer_chart_selection,
          data: data.top_repeated_customer_chart_data,
          options: {
            maintainAspectRatio: false,

            onClick: (evt, elements) => {
              if (elements.length > 0) {
                const element = elements[0];
                const clickedIndex = element.index;
                const clickedLabel = data.top_repeated_customer_chart_data.labels[clickedIndex];
                const clickedValue = data.top_repeated_customer_chart_data.datasets[0].detail[clickedIndex]
                var options = {
                };
                self.action.doAction({
                  name: _t(clickedLabel),
                  type: 'ir.actions.act_window',
                  res_model: 'dev.repair.request',
                  domain: [["id", "in", clickedValue]],
                  view_mode: 'list,form',
                  views: [
                    [false, 'list'],
                    [false, 'form']
                  ],
                  target: 'current'
                }, options)
              } else {
              }
            }
          }
        });
      });
  }

  // Lead List
  async render_garage_lead_list(rowsPerPage, page) {
    var user_selection = document.querySelector('#user_selection').value;
    var customer_selection = document.querySelector('#customer_selection').value;
    var duration_selection = document.querySelector('#request_date').value;
    self = this
    await rpc("/garage/lead/list/data", {
      'data':
      {
          'user_id': user_selection,
          'partner_id': customer_selection,
          'duration':duration_selection,
      }
    }).then(function (data) {
      self.state.garage_lead_list = data['garage_lead_ids'];
      var tbody = document.querySelector("#all_garage_lead_lst tbody");
      tbody.innerHTML = '';
      self.state.garage_lead_list_length = self.state.garage_lead_list.length
      const start = (page - 1) * rowsPerPage;
      const end = start + rowsPerPage;
      const paginatedData = self.state.garage_lead_list.slice(start, end)
      for (var i = 0; i < paginatedData.length; i++) {
        var row = document.createElement("tr");
        for (var key in paginatedData[i]) {
          if (key !== 'id') {
            var cell = document.createElement("td");
            if (paginatedData[i][key].length == 2) {
              cell.textContent = paginatedData[i][key][1];
              row.appendChild(cell);
            }
            else if (key === 'create_date') {
              var cell = document.createElement("td");
              var date = paginatedData[i]['create_date']
              if (date) {
                var date_splited = date.split(' ')[0].split('-');
                cell.textContent = date_splited[2] + '-' + date_splited[1] + '-' + date_splited[0];
              }
              else {
                cell.textContent = '-'
              }
              row.appendChild(cell);
            }


            else {
              if (paginatedData[i][key] == false) {
                cell.textContent = '-';
                row.appendChild(cell);
              }
              else {
                cell.textContent = paginatedData[i][key];
                row.appendChild(cell);
              }
            }
          }
        }
        var buttonCell = document.createElement("td");
        var button = document.createElement("button");
        button.textContent = "View";
        button.className = "btn-primary rounded p-2";
        button.style.border = "none";
        button.style.backgroundColor = "#71639E"; // Set background color to purple
        button.style.color = "white";

        button.setAttribute("data-id", paginatedData[i].id);
        button.addEventListener("click", function () {
          var id = this.getAttribute("data-id");
          // Call your function with the ID
          garage_lead_tree_button_function(id);
        });
        buttonCell.appendChild(button);
        row.appendChild(buttonCell);
        tbody.appendChild(row);
      }

      function garage_lead_tree_button_function(id) {
        var options = {
        };
        self.action.doAction({
          name: _t("Lead"),
          type: 'ir.actions.act_window',
          res_model: 'crm.lead',
          domain: [["id", "=", id]],
          view_mode: 'list,form',
          views: [
            [false, 'list'],
            [false, 'form']
          ],
          target: 'current'
        }, options)

      }
    });
  }

  lead_PrevPage(e) {
    if (this.state.current_garage_lead_page > 1) {
      this.state.current_garage_lead_page--;
      this.render_garage_lead_list(this.state.rowsPerPage, this.state.current_garage_lead_page);
      document.getElementById("lead_next_button").disabled = false;
    }
    if (this.state.current_garage_lead_page == 1) {
      document.getElementById("lead_prev_button").disabled = true;
    } else {
      document.getElementById("lead_prev_button").disabled = false;
    }
  }

  lead_NextPage() {
    if ((this.state.current_garage_lead_page * this.state.rowsPerPage) < this.state.garage_lead_list_length) {
      this.state.current_garage_lead_page++;
      this.render_garage_lead_list(this.state.rowsPerPage, this.state.current_garage_lead_page);
      document.getElementById("lead_prev_button").disabled = false;
    }
    if (Math.ceil(this.state.garage_lead_list_length / this.state.rowsPerPage) == this.state.garage_lead_list_length) {
      document.getElementById("lead_next_button").disabled = true;
    } else {
      document.getElementById("lead_next_button").disabled = false;
    }
  }


  // Due Invoice List

  async render_garage_due_invoice_list(rowsPerPage, page) {
    var user_selection = document.querySelector('#user_selection').value;
    var customer_selection = document.querySelector('#customer_selection').value;
    var duration_selection = document.querySelector('#request_date').value;
    self = this
    await rpc("/due/invoice/list/data", {
      'data':
      {
          'user_id': user_selection,
          'partner_id': customer_selection,
          'duration':duration_selection,
      }
    }).then(function (data) {
      self.state.garage_due_invoice_list = data['due_invoice_ids'];
      var tbody = document.querySelector("#all_garage_due_invoice_lst tbody");
      tbody.innerHTML = '';
      self.state.garage_due_invoice_list_length = self.state.garage_due_invoice_list.length
      const start = (page - 1) * rowsPerPage;
      const end = start + rowsPerPage;
      const paginatedData = self.state.garage_due_invoice_list.slice(start, end)
      for (var i = 0; i < paginatedData.length; i++) {
        var row = document.createElement("tr");
        for (var key in paginatedData[i]) {
          if (key !== 'id') {
            var cell = document.createElement("td");
            if (paginatedData[i][key].length == 2) {
              cell.textContent = paginatedData[i][key][1];
              row.appendChild(cell);
            }
            else if (key === 'invoice_date') {
              var cell = document.createElement("td");
              var date = paginatedData[i]['invoice_date']
              if (date) {
                var date_splited = date.split(' ')[0].split('-');
                cell.textContent = date_splited[2] + '-' + date_splited[1] + '-' + date_splited[0];
              }
              else {
                cell.textContent = '-'
              }
              row.appendChild(cell);
            }


            else {
              if (paginatedData[i][key] == false) {
                cell.textContent = '-';
                row.appendChild(cell);
              }
              else {
                cell.textContent = paginatedData[i][key];
                row.appendChild(cell);
              }
            }
          }
        }
        var buttonCell = document.createElement("td");
        var button = document.createElement("button");
        button.textContent = "View";
        button.className = "btn-primary rounded p-2";
        button.style.border = "none";
        button.style.backgroundColor = "#71639E"; // Set background color to purple
        button.style.color = "white";

        button.setAttribute("data-id", paginatedData[i].id);
        button.addEventListener("click", function () {
          var id = this.getAttribute("data-id");
          // Call your function with the ID
          garage_due_invoice_tree_button_function(id);
        });
        buttonCell.appendChild(button);
        row.appendChild(buttonCell);
        tbody.appendChild(row);
      }

      function garage_due_invoice_tree_button_function(id) {
        var options = {
        };
        self.action.doAction({
          name: _t("Due Invoice"),
          type: 'ir.actions.act_window',
          res_model: 'account.move',
          domain: [["id", "=", id]],
          view_mode: 'list,form',
          views: [
            [false, 'list'],
            [false, 'form']
          ],
          target: 'current'
        }, options)

      }
    });
  }

  due_invoice_PrevPage(e) {
    if (this.state.current_garage_due_invoice_page > 1) {
      this.state.current_garage_due_invoice_page--;
      this.render_garage_due_invoice_list(this.state.rowsPerPage, this.state.current_garage_due_invoice_page);
      document.getElementById("due_invoice_next_button").disabled = false;
    }
    if (this.state.current_garage_due_invoice_page == 1) {
      document.getElementById("due_invoice_prev_button").disabled = true;
    } else {
      document.getElementById("due_invoice_prev_button").disabled = false;
    }
  }

  due_invoice_NextPage() {
    if ((this.state.current_garage_due_invoice_page * this.state.rowsPerPage) < this.state.garage_due_invoice_list_length) {
      this.state.current_garage_due_invoice_page++;
      this.render_garage_due_invoice_list(this.state.rowsPerPage, this.state.current_garage_due_invoice_page);
      document.getElementById("due_invoice_prev_button").disabled = false;
    }
    if (Math.ceil(this.state.garage_due_invoice_list_length / this.state.rowsPerPage) == this.state.garage_due_invoice_list_length) {
      document.getElementById("due_invoice_next_button").disabled = true;
    } else {
      document.getElementById("due_invoice_next_button").disabled = false;
    }
  }

  // Paid Invoice List
  async render_garage_paid_invoice_list(rowsPerPage, page) {
    // var room_type_selection = document.querySelector('#room_type_selection').value;
    self = this
    await rpc("/paid/invoice/list/data", {
      'data':
      {
        // 'room_type': room_type_selection,
      }
    }).then(function (data) {
      self.state.garage_paid_invoice_list = data['paid_invoice_ids'];
      var tbody = document.querySelector("#all_garage_paid_invoice_lst tbody");
      tbody.innerHTML = '';
      self.state.garage_paid_invoice_list_length = self.state.garage_paid_invoice_list.length
      const start = (page - 1) * rowsPerPage;
      const end = start + rowsPerPage;
      const paginatedData = self.state.garage_paid_invoice_list.slice(start, end)
      for (var i = 0; i < paginatedData.length; i++) {
        var row = document.createElement("tr");
        for (var key in paginatedData[i]) {
          if (key !== 'id') {
            var cell = document.createElement("td");
            if (paginatedData[i][key].length == 2) {
              cell.textContent = paginatedData[i][key][1];
              row.appendChild(cell);
            }
            else if (key === 'invoice_date') {
              var cell = document.createElement("td");
              var date = paginatedData[i]['invoice_date']
              if (date) {
                var date_splited = date.split(' ')[0].split('-');
                cell.textContent = date_splited[2] + '-' + date_splited[1] + '-' + date_splited[0];
              }
              else {
                cell.textContent = '-'
              }
              row.appendChild(cell);
            }


            else {
              if (paginatedData[i][key] == false) {
                cell.textContent = '-';
                row.appendChild(cell);
              }
              else {
                cell.textContent = paginatedData[i][key];
                row.appendChild(cell);
              }
            }
          }
        }
        var buttonCell = document.createElement("td");
        var button = document.createElement("button");
        button.textContent = "View";
        button.className = "btn-primary rounded p-2";
        button.style.border = "none";
        button.style.backgroundColor = "#71639E"; // Set background color to purple
        button.style.color = "white";

        button.setAttribute("data-id", paginatedData[i].id);
        button.addEventListener("click", function () {
          var id = this.getAttribute("data-id");
          // Call your function with the ID
          garage_paid_invoice_tree_button_function(id);
        });
        buttonCell.appendChild(button);
        row.appendChild(buttonCell);
        tbody.appendChild(row);
      }

      function garage_paid_invoice_tree_button_function(id) {
        var options = {
        };
        self.action.doAction({
          name: _t("Paid Invoice"),
          type: 'ir.actions.act_window',
          res_model: 'account.move',
          domain: [["id", "=", id]],
          view_mode: 'list,form',
          views: [
            [false, 'list'],
            [false, 'form']
          ],
          target: 'current'
        }, options)

      }
    });
  }

  paid_invoice_PrevPage(e) {
    if (this.state.current_garage_paid_invoice_page > 1) {
      this.state.current_garage_paid_invoice_page--;
      this.render_garage_paid_invoice_list(this.state.rowsPerPage, this.state.current_garage_paid_invoice_page);
      document.getElementById("paid_invoice_next_button").disabled = false;
    }
    if (this.state.current_garage_paid_invoice_page == 1) {
      document.getElementById("paid_invoice_prev_button").disabled = true;
    } else {
      document.getElementById("paid_invoice_prev_button").disabled = false;
    }
  }

  paid_invoice_NextPage() {
    if ((this.state.current_garage_paid_invoice_page * this.state.rowsPerPage) < this.state.garage_paid_invoice_list_length) {
      this.state.current_garage_paid_invoice_page++;
      this.render_garage_paid_invoice_list(this.state.rowsPerPage, this.state.current_garage_paid_invoice_page);
      document.getElementById("paid_invoice_prev_button").disabled = false;
    }
    if (Math.ceil(this.state.garage_paid_invoice_list_length / this.state.rowsPerPage) == this.state.garage_paid_invoice_list_length) {
      document.getElementById("paid_invoice_next_button").disabled = true;
    } else {
      document.getElementById("paid_invoice_next_button").disabled = false;
    }
  }

  // Onclick action for counter
  action_all_garage_counter(e) {
    e.stopPropagation();
    e.preventDefault();
    var cont = { search_default_no_share: true };
    var options = {
      on_reverse_breadcrumb: this.on_reverse_breadcrumb,
    };
    var rec_id = e.currentTarget.getAttribute('rec-id');
    var action = e.currentTarget.id || false;
    var domain = false;
    cont = {
      search_default_no_share: true,
      search_default_group_by_state: true,
    }
    var title_name = ' ';
    var res_model = ' ';

    if (action == 'total_lead_id') {
      domain = [["id", "in", this.state.total_lead_ids]];
      title_name = 'Total Lead',
        res_model = 'crm.lead'

    }
    else if (action == 'total_won_lead_id') {
      domain = [["id", "in", this.state.total_won_lead_ids]];
      title_name = 'Won Lead',
        res_model = 'crm.lead'

    }
    else if (action == 'total_rfq_id') {
      domain = [["id", "in", this.state.total_rfq_list]];
      title_name = 'RFQ',
        res_model = 'purchase.order'
    }
    else if (action == 'total_work_order_id') {
      domain = [["id", "in", this.state.total_work_order_list]]
      title_name = 'Work Order',
        res_model = 'project.task'
    }
    
    else if (action == 'total_sale_id') {
      console.log(" this.state.total_sale_list================", this.state.total_sale_list)
      domain = [["id", "in", this.state.total_sale_list]]
      title_name = 'Total Sales',
        res_model = 'sale.order'
    }
    else if (action == 'total_invoice_id') {
      domain = [["id", "in", this.state.total_invoice_list]]
      title_name = 'Paid Invoice',
        res_model = 'account.move'
    }
    else if (action == 'total_due_invoice_id') {
      domain = [["id", "in", this.state.total_due_invoice_list]]
      title_name = 'Due Invoice',
        res_model = 'account.move'
    }
    else if (action == 'total_request_id') {
      domain = [["id", "in", this.state.total_request]]
      title_name = 'Request',
        res_model = 'dev.repair.request'
    }

    else if (action == 'total_draft_job_card_id') {
      domain = [["id", "in", this.state.draft_job_card_list]]
      title_name = 'Job Card',
        res_model = 'dev.repair.request'
    }
    else if (action == 'total_confirm_job_card_id') {
      domain = [["id", "in", this.state.confirm_job_card_list]]
      title_name = 'Job Card ',
        res_model = 'dev.repair.request'
    }
    else if (action == 'total_in_process_job_card_id') {
      domain = [["id", "in", this.state.in_process_job_card_list]]
      title_name = 'Job Card ',
        res_model = 'dev.repair.request'
    }
    else if (action == 'total_diagnosis_id') {
      domain = [["id", "in", this.state.total_diagnosis_list]]
      title_name = 'Diagnosis ',
        res_model = 'project.task'
    }
    else if (rec_id != 'undefined') {
      domain = [["id", "=", rec_id]]
    }
    this.action.doAction({
      name: _t(title_name),
      type: 'ir.actions.act_window',
      res_model: res_model,
      domain: domain,
      view_mode: 'list,form',
      context: cont,
      views: [
        [false, 'list'],
        [false, 'form']
      ],
      target: 'current'
    }, options)
  }


  render_garage_filter() {
    rpc('/garage/all_filter').then(function (data) {
      var users = data[0]
      users?.forEach(user => {
        const option = document.createElement('option');
        option.value = user?.id;
        option.textContent = user?.name;
        document.querySelector('#user_selection')?.appendChild(option);
      });

      var customers = data[1]
      customers?.forEach(customer => {
        const option = document.createElement('option');
        option.value = customer?.id;
        option.textContent = customer?.name;
        document.querySelector('#customer_selection')?.appendChild(option);
      });
    })
  }

  async getCardData() {
    var self = this;
    var data = await rpc('/get/garage/tiles/data')

    self.state.total_won_lead_ids = data['total_won_lead']
    self.state.total_lead_ids = data['total_lead']
    self.state.total_work_order_list = data['total_work_order']
    self.state.total_due_invoice_list = data['due_invoice_list'],
      self.state.total_invoice_list = data['paid_invoice_list'],
      self.state.total_request = data['total_request'],
      self.state.draft_job_card_list = data['draft_job_card'],
      self.state.confirm_job_card_list = data['confirm_job_card'],
      self.state.in_process_job_card_list = data['in_process_job_card'],
      self.state.total_diagnosis_list = data['total_diagnosis'],
      self.state.total_rfq_list = data['total_rfq'],
      self.state.total_sale_list = data['total_sales_ids'],
      
      self.state.user_name.value = data['user_name'],
      self.state.user_img.value = data['user_img']

  }
}

garageAnalysisDashboard.template = "garageAnalysisDashboard"
registry.category("actions").add("garage_dashboard", garageAnalysisDashboard)
