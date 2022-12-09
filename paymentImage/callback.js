const queryString = window.location.search;

const urlParams = new URLSearchParams(queryString);

const token = urlParams.get('token')

console.log(token)

fetch("http://localhost:5000/payment?token=" + token)
    .then((response) => {
        if (response.ok) {
            return response.json();
        } else {
        throw new Error("NETWORK RESPONSE ERROR");
        }
  })
    .then(data => {
        console.log(data)
        console.log(typeof(data))
        
        let paymentStatus = data["payment_status"]
        let sessionStatus = data["status"]
        let url = data["url"]
        console.log(url)
        console.log(sessionStatus)
        console.log(paymentStatus)

        
        
        if (sessionStatus === "complete" && paymentStatus === "paid"){
            document.getElementById("paymentStatus").innerHTML = "Payment Success"
            document.getElementById("payment_header").style.backgroundColor = "green"
            document.getElementById("icon").className = "fa fa-check"
            const payURL = document.getElementsByClassName("content")[0]
            payURL.insertAdjacentHTML("beforeend", '<a href="#">Go to Home</a>')
        }
        if(sessionStatus === "open" && paymentStatus === "unpaid"){
            document.getElementById("paymentStatus").innerHTML = "You have not yet paid"
            document.getElementById("payment_header").style.backgroundColor = "orange"
            document.getElementById("icon").className = "fa fa-dollar"
            const payURL = document.getElementsByClassName("content")[0]
            payURL.insertAdjacentHTML("beforeend", '<a href="#">Go to Home</a> <a href=' + url + '>Pay with Stripe now</a>')
        }
        if(sessionStatus === "expired" && paymentStatus === "unpaid"){
            document.getElementById("paymentStatus").innerHTML = "Your session has expired"
            document.getElementById("payment_header").style.backgroundColor = "red"
            document.getElementById("icon").className = "fa fa-clock-o"
            const payURL = document.getElementsByClassName("content")[0]
            payURL.insertAdjacentHTML("beforeend", '<a href="#">Go to Home</a>')
        }




        


  })
    .catch((error) => console.error("FETCH ERROR:", error));

