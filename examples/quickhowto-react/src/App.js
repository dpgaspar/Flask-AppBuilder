import React, { Component } from 'react';
import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import Table from './components/Table';
import axios from 'axios';


class App extends Component {


    render() {
        return (
              <div className="container">
                   <h1>React FAB2 Experiment</h1>
                   <Table
                    resource='contactmodelapi'
                   >
                   </Table>
              </div>
            );
    }
}

export default App;
