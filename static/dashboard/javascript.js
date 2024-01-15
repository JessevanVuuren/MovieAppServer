const host_url = window.location.host
const protocol = window.location.protocol === "https:" ? "wss://" : "ws://"
const wss_url = protocol + host_url + window.DASHBOARD_URL_MOVIE_APP + "-wss"
console.log(wss_url)

const users = document.getElementById("users_amount")
const rooms = document.getElementById("rooms_amount")

const webSocket = new WebSocket(wss_url);
webSocket.onmessage = async (data) => {
  const message = await JSON.parse(data.data)
  console.log(message)

  if (message.success) {
    users.innerText = message.payload.amount_users
    rooms.innerText = message.payload.amount_rooms
  } else {
    if (message.error == "wrong password") {
      window.location.href = "/"
    }
  }
}

webSocket.onopen = async = (data) => {
  get_dashboard_password()
}

const get_dashboard_password = () => {
  const return_value = prompt("Password:");
  console.log(return_value)
  if (!return_value) get_dashboard_password()
  webSocket.send(JSON.stringify({password: return_value}))
}

