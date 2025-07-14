// import { Chart } from "frappe-charts"

frappe.ready(function () {

  const assets = [
    'assets/frappe/js/lib/socket.io.min.js',
    'assets/frappe/js/frappe/socketio_client.js'
  ];

  frappe.require(assets, () => {
    // ini Vue app
    const { createApp } = Vue
    // init chart element 

    var currentTeam = window.location.hash;

    if (!currentTeam) {
      currentTeam = '#combine';
    }

    if (window.dev_server) {
      frappe.boot.socketio_port = window.socketio_port //use socketio port shown when bench starts
    }
    // init socket.io
    frappe.socketio.init();

    var voteChart = null;
    var voteChartLatitude = null;
    var voteChartLongitude = null;

    var barColors = ["green", "blue", "orange", "brown", "red"];

    var updateVoteChart = function (chart, data) {
      chart.data.labels = data.labels;
      chart.data.datasets[0].data = data.values;
      chart.update();
    };

    // Sweet Alert 2
    var swalWithBootstrapButtons = Swal.mixin({
      customClass: {
        confirmButton: 'btn btn-success',
        cancelButton: 'btn btn-danger'
      },
      buttonsStyling: false
    })

    createApp({
      data() {
        return {
          activeTeam: currentTeam,
          activeUser: 'Guest',
          dataLoaded: false,
          showResult: false,
          employees: [],
          voters: [],
          total_votes_today: 0,
          total_votes_today_latitude: 0,
          total_votes_today_longitude: 0,
          voted: '',
          loginForm: { usr: '', pwd: '' },
          loginError: ''
        }
      },

      delimiters: ['[[', ']]'],

      mounted() {
        frappe.realtime.on('vote_updated', (eventData) => {
          // this.update_vote_data(eventData.vote_count, eventData.total_votes[0]);
          this.total_votes_today = eventData.total_votes[0].total_votes;
          let chart_values = this.create_chart_labels_and_values(eventData.vote_count);

          if (voteChart) {
            updateVoteChart(voteChart, chart_values);
          } else {
            voteChart = new Chart(this.$refs.chartContainer, {
              type: "polarArea",
              data: {
                labels: chart_values.labels,
                datasets: [{
                  backgroundColor: barColors,
                  data: chart_values.values
                }]
              },
              options: {}
            });
          }

        });

        frappe.realtime.on('vote_updated_latitude', (eventData) => {
          this.total_votes_today_latitude = eventData.total_votes[0].total_votes;
          let chart_values = this.create_chart_labels_and_values(eventData.vote_count);

          if (voteChartLatitude) {
            updateVoteChart(voteChartLatitude, chart_values);
          } else {
            voteChartLatitude = new Chart(this.$refs.chartContainerLatitude, {
              type: "polarArea",
              data: {
                labels: chart_values.labels,
                datasets: [{
                  backgroundColor: barColors,
                  data: chart_values.values
                }]
              },
              options: {}
            });
          }

        });

        frappe.realtime.on('vote_updated_longitude', (eventData) => {
          // this.update_vote_data(eventData.vote_count, eventData.total_votes[0]);
          this.total_votes_today_longitude = eventData.total_votes[0].total_votes;
          let chart_values = this.create_chart_labels_and_values(eventData.vote_count);

          if (voteChartLongitude) {
            updateVoteChart(voteChartLongitude, chart_values);
          } else {
            voteChartLongitude = new Chart(this.$refs.chartContainerLongitude, {
              type: "polarArea",
              data: {
                labels: chart_values.labels,
                datasets: [{
                  backgroundColor: barColors,
                  data: chart_values.values
                }]
              },
              options: {}
            });
          }

        });

        this.getEmployeeList();
      },

      computed: {
        list_title() {
          let title = '';
          if (this.activeTeam == '#latitude') {
            title = 'Latitude';
          } else if (this.activeTeam == '#longitude') {
            title = 'Longitude';
          } else {
            title = 'Combine PS';
          }
          return title;
        }
      },

      methods: {
        create_chart_labels_and_values(vote_count) {
          let chartLabels = [];
          let chartValues = [];

          var push_values = (label, value) => {
            chartLabels.push(label);
            chartValues.push(value);
          }

          vote_count.forEach((vote) => {
            push_values(vote.employee, vote.votes_today);
          });

          return { 'labels': chartLabels, 'values': chartValues }
        },

        get_result() {
          this.getEmployeeList();
          this.showResult = true;
        },

        loginUser() {
          frappe.call({ method: 'sydani.www.vote.index.login', args: this.loginForm })
            .then((res) => {
              if (res.message.success_key == 0) {
                this.loginError = "Login Failed";
                setTimeout(() => {
                  this.loginError = "";
                }, 3000)
              } else if (res.message.success_key == 1) {
                // localStorage.activeUser = res.message.user;
                this.activeUser = res.message.user;
                this.getEmployeeList();
              }
            });
        },

        getEmployeeList() {
          frappe.call({ method: 'sydani.www.vote.index.get_employee_list', args: { 'team': this.activeTeam } })
            .then((res) => {
              if (res.message == 'Guest') {
                this.activeUser = res.message;
              } else {
                this.activeUser = res.message.user;
                this.employees = res.message.employees;
              }
            });
        },

        // Not using this code below
        datachnaged() {
          // this.updateChartData(voteChart, { data: 33, label: 'Argentina' });
        },

        changeTeam(team) {
          this.activeTeam = team;
          this.getEmployeeList()
        },

        employeeVoted(employee) {
          swalWithBootstrapButtons.fire({
            title: `Vote for ${employee.name}`,
            text: "You won't be able to revert this!",
            icon: 'success',
            showCancelButton: true,
            confirmButtonText: 'Yes, Vote!',
            cancelButtonText: 'No, cancel!',
            reverseButtons: true
          }).then((result) => {
            if (result.isConfirmed) {
              // this.voted = employee.email;
              frappe.call({
                method: 'sydani.www.vote.index.cast_vote', args: {
                  employee_voted: employee, ps_team: this.activeTeam, user_email: this.activeUser
                }
              })
                .then(res => {
                  if (res.message.success_key == 1) {
                    swalWithBootstrapButtons.fire(
                      'Voted',
                      'Your vote submited',
                      'success'
                    )
                  } else {
                    swalWithBootstrapButtons.fire(
                      'Vote Cancelled',
                      res.message.message,
                      'error'
                    )
                  }
                });
            } else if (
              /* Read more about handling dismissals below */
              result.dismiss === Swal.DismissReason.cancel
            ) {
              swalWithBootstrapButtons.fire(
                'Vote Cancelled',
                'You can change your vote',
                'error'
              )
            }
          })
        },
      }
    }).mount('#vue-app')
  });
});