app.controller('projectsController', ['$scope', '$http','$sce', function($scope, $http,$sce) {
    $scope.listData=[];
    $scope.logData=[];
    $scope.projects={};
    $scope.parsedURL="";
    $scope.customUrl = $sce.trustAsResourceUrl('http://jsfiddle.net/478wA/');

    /*
     The code below will load the Json data into designed data structure for my web page
     */
    $http.get('./data/svn_list.json')
        .success(function(listData) {
            $scope.listData = listData["lists"]["list"]["entry"];
            path = listData["lists"]["list"]["_path"];
            $scope.parsedURL=path;
            $scope.getInfo($scope.listData);
            $scope.addFile($scope.listData);
            $http.get('./data/svn_log.json')
                .success(function(logData) {
                    $scope.logData = logData["log"]["logentry"];
                    $scope.matchInfo($scope.logData);
                });

            console.log($scope.projects);
        });

    /*
     The code below will add the most recent version of assignment into my structure
     */
    $scope.getInfo = function(data){
        for (var i = 0; i < data.length; i++)
        {
            var name = data[i]['name'];
            var date = data[i]['commit']['date'];
            if (name.indexOf("/") >= 0) {
                name = name.slice(0, name.indexOf("/"));
            }
            if ((name in $scope.projects && $scope.projects[name][date]<date)||(!(name in $scope.projects))) {
                var newProject={};
                newProject["name"] = name;
                newProject["date"]= date;
                newProject["kind"] = data[i]['_kind'];
                newProject["author"] = data[i]['commit']['author'];
                newProject["version"] = data[i]['commit']['_revision'];
                newProject["files"] = {};
                newProject["comments"] = "";
                $scope.projects[name]=newProject;
            }
        }
    };

    /*
     The code below will create a new file object
     */
    function createNewFileEntry(newFile, filename, file_version, data, i) {
        newFile["fileName"] = filename;
        newFile["Version"] = file_version;
        newFile["Date"] = data[i]['commit']['date'];
        newFile["Size"] = data[i]["size"];
        newFile["msg"] = "";
        newFile["Author"] = data[i]['commit']['author'];
        if (data[i]["name"].lastIndexOf("src") >= 0) {
            newFile["Type"] = "Src";
        }
        else if (data[i]["name"].lastIndexOf("png") >= 0) {
            newFile["Type"] = "Img";
        }
        else {
            newFile["Type"] = "File";
        }
        newFile["Path"] = path + "/" + data[i]["name"];
    }

    /*
     The code below will add files under each assignment
     */
    $scope.addFile = function(data){
        for (var i = 0; i < data.length; i++)
        {
            var name = data[i]['name'];
            if (name.indexOf("/") >= 0) {
                name = name.slice(0, name.indexOf("/"));
            }
            var filename = data[i]['name'];
            if (filename.lastIndexOf("/") >= 0) {
                filename = filename.slice(filename.lastIndexOf("/")+1, filename.length);
            }
            var file_version = data[i]['commit']['_revision'];
            if(!(filename in $scope.projects[name]["files"]))
            {
                if("size" in data[i]){
                    var newFile = {};
                    createNewFileEntry(newFile, filename, file_version, data, i);

                    newFile["PreviousVersion"] = {};
                    $scope.projects[name]["files"][filename] = newFile;
                }
            }
            else if(filename in $scope.projects[name]["files"])
            {
                if($scope.projects[name]["files"][filename]["Version"]<file_version)
                {
                    var newFile = {};
                    createNewFileEntry(newFile, filename, file_version, data, i);

                    newFile["PreviousVersion"] = $scope.projects[name]["files"][filename]["PreviousVersion"];
                    var oldVersion = $scope.projects[name]["files"][filename]["Version"];
                    $scope.projects[name]["files"][filename]["PreviousVersion"]={};
                    newFile["PreviousVersion"][oldVersion] = $scope.projects[name]["files"][filename];
                    $scope.projects[name]["files"][filename] = newFile;
                }
                else
                {
                    var newFile = {};
                    createNewFileEntry(newFile, filename, file_version, data, i);

                    newFile["PreviousVersion"] = {};
                    $scope.projects[name]["files"][filename]["PreviousVersion"][file_version] = newFile;
                }
            }


        }
    };

    /*
     The code below will add the comment message into the designed structure
     */
    $scope.matchInfo = function(data){
        for (var i = 0; i < data.length; i++)
        {

            var version = data[i]["_revision"];
            for (var j in $scope.projects)
            {
                if(version === $scope.projects[j]["version"])
                {
                    $scope.projects[j]["comments"]=$scope.logData[i]["msg"];
                }
            }
        }
    };

    /*
     The code will set up the URL for the iframe
     */
    $scope.setURL = function (key) {
        $scope.iframeTitle=key;
        $scope.parsedURL=key;
        $scope.customUrl = $sce.trustAsResourceUrl($scope.parsedURL);
    };
}]);
