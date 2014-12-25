/**
 * Created by Kyl on 12/24/2014.
 */


var headToHeadController = angular.module('headToHeadController', []);

var sled = angular.module('sled', [
    'headToHeadController'
]);

headToHeadController.controller('HeadToHead', [
    '$scope',
    '$http',
    function($scope, $http){
        var teamsObj = loadTeamsObj();
        var predictionsObj = loadPredictionObj();

        var home = $('#homeTypeahead');
        var away = $('#awayTypeahead');

        var homeTeam = null;
        var awayTeam = null;

        $scope.teams = teamsObj;
        $scope.predictions = predictionsObj;

        setupTypeaheads();

        function loadTeamsObj()
        {
            var rawArr = JSON.parse($('#teamsData').text());
            return _.map(rawArr, function(o){
                return {
                    id: o[0],
                    name: o[1]
                };
            });
        }

        function loadPredictionObj()
        {
            var rawArr = JSON.parse($('#predictionsData').text());
            var dict = {};
            _.each(rawArr, function(o){
                if ( !dict[o[0]] )
                    dict[o[0]] = {};

                dict[o[0]][o[1]] = o[2];
            });

            return dict;
        }

        function teamsDataset(query, cb)
        {
            var subset = _.filter(teamsObj, function(o){
                return o.name.toLowerCase().indexOf(query.toLowerCase()) == 0;
            });

            cb(subset);
        }

        function setupTypeaheads()
        {
            var dataSet = {
                source:teamsDataset,
                name:'teams',
                displayKey:'name'
            };

            home.typeahead({
                highlight:false,
                hint:true,
                minLength:3
            },dataSet)
                .on('typeahead:selected', function(event, suggestion){
                    event.preventDefault();
                    event.stopPropagation();
                    homeTeam = suggestion;
                    getLine();
                    home.typeahead('destroy');
                    away.typeahead('destroy');
                    setupTypeaheads();
                })
                .on('typeahead:autocompleted', function(event, suggestion){
                    homeTeam = suggestion;
                    getLine();
                });

            away.typeahead({
                highlight:false,
                hint:true,
                minLength:3
            },dataSet)
                .on('typeahead:selected', function(event, suggestion){
                    event.preventDefault();
                    event.stopPropagation();
                    awayTeam = suggestion;
                    getLine();
                    home.typeahead('destroy');
                    away.typeahead('destroy');
                    setupTypeaheads();
                })
                .on('typeahead:autocompleted', function(event, suggestion){
                    awayTeam = suggestion;
                    getLine();
                });
        }

        function getLine()
        {
            if ( homeTeam && awayTeam )
            {
                $scope.$apply(function(){
                    $scope.line = $scope.predictions[homeTeam.id][awayTeam.id];
                });
            }
            else
            {
                $scope.$apply(function(){
                    $scope.line = '';
                });
            }
        }
    }
]);


