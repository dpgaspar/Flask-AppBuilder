import React, { Component } from 'react';
//import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import CRUDTable from './components/Table';


class App extends Component {
  render() {
    return (
      <div className="container">
        <CRUDTable resource={this.props.match.params.resource}>
        </CRUDTable>
      </div>
    );
  }
}

export default App;
