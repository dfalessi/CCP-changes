<!DOCTYPE html>
<html lang="en">
  <head>
      <title>SURP 2017 App</title>
      <meta charset="utf-8">
      <meta name="description" content="Testing bootstrap here!">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
      <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
  </head>
  <body>
    <div class="container">
      <p></p>
      <p>Upload .xml file here</p>
      <button onclick="getXml()">Upload</button>
      <p id = "name"></p>
      <script>
        function getXml() {
          var fileName = "File name will be displayed here after uploading";
          document.getElementById("name").innerHTML = fileName;
        }
      </script>
    </div>
    <div class="container">

    </div>
    <div class="container">
      <button onclick="displaySnapshots()">Display snapshots</button>
      <p id="title"></p>
      <div id="table"></div>
      <script>
        function displaySnapshots() {
          var title = "<h2>Snapshots</h2>";
          document.getElementById("title").innerHTML = title;
          //document.write(title);
          var stats = [
            "Date Created",
            "Project Name",
            "Revision",
          ];

          var table = "<table class = \"table table-bordered\"><thead><tr>";
          for (var i = 0; i < stats.length; i++) {
            table += "<th>" + stats[i] + "</th>";
          }
          table += "</tr></thead></table>";
          document.getElementById("table").innerHTML = table;
          //document.write(table);
        }
      </script>
    </div>
  </body>
</html>