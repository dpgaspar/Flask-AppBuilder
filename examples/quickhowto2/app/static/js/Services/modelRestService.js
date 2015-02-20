
app.service("modelRestService", function($http, $q) {

	//return public API
	//
	return({
		query: query,
		create: create,
		update: update,
		remove: remove
	});

	function query(modelview_name, base_url, filter, order_column, order_direction, page, page_size) {
		var query_string = "";
		var get_params = {};
		if (filter != "" ) {
	        get_params['_flt_0_name'] = filter;
      	      	}
	      	if (order_column != "") {
        		get_params['_oc_' + modelview_name] = order_column;
	        	get_params['_od_' + modelview_name] = order_direction;
              	}
                if (page) {
			get_params['_page_' + modelview_name] = page;
		} 
                if (page_size) {
			get_params['_psize_' + modelview_name] = page_size;
		}
	      	console.log("GET", get_params);
      	      	var request = $http.get(base_url, { params : get_params });
              	return(request.then(handleSuccess, handleError ));
	}

	function remove(base_url, pk) {
		$http.delete(base_url + '/' + pk)
		return( request.then( handleSuccess, handleError ) );
	}

	function create(base_url) {
		$http.post(base_url + '/' + pk)
		return( request.then( handleSuccess, handleError ) );
	}

	function update(base_url, pk) {
		$http.put(base_url + '/' + pk)
		return( request.then( handleSuccess, handleError ) );
	}


        // PRIVATE METHODS
        //
        function handleError( response ) {
                if (!angular.isObject( response.data ) || !response.data.message) {
                    return($q.reject( "An unknown error occurred." ));
                }
                return($q.reject(response.data.message ));
        }

        function handleSuccess( response ) {
            return( response.data );
	    }
}
);
