import axios from 'axios'


const apiVersion = 'v1';
const apiUrl = `/api/${apiVersion}`;

class Api {

  constructor(height, width) {
    this.client = axios.create({ baseURL: apiUrl });
  }

  get(resource, filters = [], order = {}) {
    var query = '';
    if (order.column !== undefined) {
      query = query + '(order_column:' + order.column + ',order_direction:' + order.direction + ')';
    }
    if (query == '') {
      return this.client.get(resource, { withCredentials: true });
    }
    else {
      return this.client.get(
        resource,
        {
          params: { q: query },
          withCredentials: true
        }
      );
    }
  }

  delete(resource, id) {
    return this.client.delete(
      resource + '/' + id,
      { withCredentials: true }
    );
  }

  info(resource) {
    return this.client.get(
      resource + '/_info',
      { withCredentials: true }
    );
  }

  getItem(resource, id) {
    return this.client.get(
      resource + '/' + id,
      { withCredentials: true }
    );
  }
}

export default Api
