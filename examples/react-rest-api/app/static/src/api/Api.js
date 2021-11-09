import axios from 'axios'
import rison from 'rison'

const apiVersion = 'v1';
const apiUrl = `/api/${apiVersion}`;

class Api {

  constructor(height, width) {
    this.client = axios.create({ baseURL: apiUrl });
  }

  get(resource, parameters) {
    let risonParameters = rison.encode(parameters);
    return this.client.get(
      resource,
      {
        params: { q: risonParameters },
        withCredentials: true
      }
    );
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

  post(resource, data) {
    return this.client.post(
      resource,
      data,
      { withCredentials: true }
    );
  }
}

export default Api
