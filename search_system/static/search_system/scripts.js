/**
 * Created by velior on 11.05.16.
 */

var app = angular.module('searchApp', ['ngCookies', 'ngMaterial', 'infinite-scroll'])
    .config([
    '$httpProvider',
    function($httpProvider) {
        // Change content type for POST so Django gets correct request object
        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
        // 2 reasons: Allows request.is_ajax() method to work in Django
        // Also, so 500 errors are returned in responses (for debugging)
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    }]).
    run([
    '$http',
    '$cookies',
    function($http, $cookies) {
        // Handles the CSRF token for POST
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    }]);

app.controller('searchController', ['$scope','$http', '$cookies',function($scope, $http) {
    $scope.searchResults = [];
    $scope.searchResultsId = -1;
    $scope.isBusy = false;
    $scope.searchRequest = "Cats";
    $scope.isLoading = false;
    $scope.search = function() {
        $scope.isLoading = true;
        $scope.searchResults = [];
        $scope.searchResultsId = -1;
        $http({
            url: '/search/',
            method: 'POST',
            data: $.param({text: $scope.searchText, requestType: "ADD"})
        }).success(function (out_data) {
            $scope.searchResultsId = out_data.result_id;
            $scope.resultAmount = out_data.result_amount;
            $scope.isLoading = false;
            $scope.loadResults();
        });
    };
    $scope.anyResults = function () {
        return $scope.searchResultsId >= 0;
    };

    $scope.loadResults = function() {
        if ($scope.searchResultsId == -1)
            return;
        $scope.isBusy = true;
        $http({
            url: '/load_results/',
            method: 'POST',
            data: $.param({resultsId: $scope.searchResultsId, requestType: "ADD"})
        }).success(function (out_data) {
            for (var i = 0; i < out_data.length; i++)
                $scope.searchResults.push(out_data[i]);
            $scope.isBusy = false;
        });

    };
    $scope.searchText = "";
    $scope.searchHistory = ['cats', 'django', 'treap implementaion c++'];
    $scope.querySearch = function() {
        var query = $scope.searchText;
        var result = [];
        if (query != "")
            results = $scope.searchHistory.filter(createFilterFor(query));
        return results;
    };
    /**
     * Create filter function for a query string
     */
    function createFilterFor(query) {
        var lowercaseQuery = angular.lowercase(query);
        return function filterFn(state) {
            return (state.indexOf(lowercaseQuery) === 0);
      };
    }

}]);