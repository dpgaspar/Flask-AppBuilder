import React, { Component } from 'react';
import axios from 'axios';

class TableHeader extends Component {

    render() {
        const row = this.props.listColumns.map(key =>
                                            <th>{this.props.labelColumns[key]}</th>)
        return (<thead><tr>{row}</tr></thead>);
    }
}

class TableRow extends Component {

    render () {
        const row = this.props.listColumns.map(key =>
                    <td>{this.props.obj[key]}</td>)
        return (
            <tr key={this.props.key}>{row}</tr>
        );
    }
}

class Table extends Component {

    constructor(props) {
          super(props);
          this.state = {data: [],
                        listColumns: [],
                        labelColumns: []};
    }

    componentDidMount(){
        axios.get('http://localhost:8080/api/v1/' + this.props.resource + '/')
              .then(response => {
                    this.setState({ data: response.data.result,
                                listColumns: response.data.list_columns,
                                labelColumns: response.data.label_columns});
              })
              .catch(function (error) {
                    console.log(error);
              })
    }

    rows(){
            const listColumns = this.state.listColumns
            return this.state.data.map(function(object, i){
                return <TableRow listColumns={listColumns} obj={object} key={i} />;
            });
    }

    render() {
        return (
            <table className="table">
                <TableHeader
                    listColumns={this.state.listColumns}
                    labelColumns={this.state.labelColumns}
                />
                <tbody>
                  {this.rows()}
                </tbody>
            </table>
        );
    }
}

export default Table;