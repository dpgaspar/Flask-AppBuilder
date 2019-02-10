import axios     from 'axios'


const apiVersion = 'v1';
const apiUrl = `http://localhost:8080/api/${apiVersion}`;

class Api {

    constructor(height, width) {
        this.client = axios.create({baseURL: apiUrl});
    }

    get(resource, filters=[], order={}, pageSize, page) {
        return this.client.get(resource)
    }
}

export default Api
