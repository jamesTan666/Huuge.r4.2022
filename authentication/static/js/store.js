

const get_all_items = "http://localhost:5000/inventory";
const login = "http://localhost:5000/login";


const app = Vue.createApp({
    computed: {
        hasItems: function () {
            return this.items.length > 0;
        }
    },
    data() {
        return {
            items: []
        };
    },
    methods: {
        getAllItems () {
            // on Vue instance created, load the book list
            const response =
                fetch(get_all_items)
                    .then(response => response.json())
                    .then(data => {
                        console.log(response);
                        if (data.code === 404) {
                            // no book in db
                            this.message = data.message;
                        } else {
                            this.items = data.data.inventories;
                            console.log(this.items);
                        }
                    })
                    .catch(error => {
                        // Errors when calling the service; such as network error,
                        // service offline, etc
                        console.log(this.message + error);

                    });

                },
        },
        login () {
            // reset data
            this.statusUpdated = false;
            this.addOrderError = "";

            let jsonData = JSON.stringify({
                order_id: this.neworder_id,
                status: this.updated_status
            });

            fetch(`${login}`,
                {
                    method: "POST",
                    headers: {
                        "Content-type": "application/json"
                    },
                    body: jsonData
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    result = data.data;
                    console.log(result);
                    // 3 cases
                    switch (data.code) {
                        case 200:
                            this.statusUpdated = true;

                            // refresh book list
                            this.getAllOrders();
                            this.neworder_id="";
                            this.updated_status="";
                            // an alternate way is to add this one element into this.books
                            break;
                        case 404:
                            this.neworder_id="";
                            this.updated_status="";
                        case 500:
                            this.addOrderError = data.message;
                            break;
                        default:
                            throw `${data.code}: ${data.message}`;
                    }
                })
        },
    
    created () {
        // on Vue instance created, load the book list
        this.getAllItems();
    }
});
const vm = app.mount('#app');