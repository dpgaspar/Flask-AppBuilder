
app.service("ApiService", function($http, $q) {

	//return public API
	//
	return({
		read: read,
		create: create,
		update: update,
		remove: remove,
        getInfo: getInfo
    });

    function getInfo(base_url) {
        var request = $http.get(base_url);
        return(request.then(handleSuccess, handleError ));
    }

	function read(modelview_name, base_url, filter, order_column, order_direction, page, page_size) {
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
		var request = $http.delete(base_url + pk);
		return( request.then( handleSuccess, handleError ) );
	}

	function create(base_url) {
		var request = $http.post(base_url + '/' + pk);
		return( request.then( handleSuccess, handleError ) );
	}

	function update(base_url, pk) {
		var request = $http.put(base_url + '/' + pk);
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


app.factory("modelRestManager", function($q, modelRestService) {

  var base_url = "";
  var config = {};

  return {
    // Load config parameters in Sync
    init: function(base_url) {
      base_url = base_url;
      $q.all([modelRestService.getInfo(base_url)]).then(function(data) {
        console.log("INIT");
        config = data;
        });
      return this;
    },

    query: function(filter, order_column, order_direction, page, page_size) {
        return modelRestService(config.modelview_name,
                            config.api_urls.read,
                            filter,
                            order_column,
                            order_direction,
                            page,
                            page_size);
    },

    getBaseUrl: function() {
      return base_url;
    },

    getConfig: function() {
        return config;
    }

  };



});

