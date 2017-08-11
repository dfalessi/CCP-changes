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
      <input type="file" id="file" onchange="return checkExtension()">
      <p id = "name"></p>
      <script>
        // some code from codexworld.com (https://www.codexworld.com/file-type-extension-validation-javascript/)
        function checkExtension() {
          var fileInput = document.getElementById("file");
          var filePath = fileInput.value;
          var allowedExtension = "xml";
          var nameSplit = filePath.split(".");
          if (nameSplit[nameSplit.length - 1] !== allowedExtension) {
            alert("Invalid file type. Please use an xml file.");
            fileInput.value = "";
            return false;
          } else {
            return true;
          }
        }
      </script>
    </div>
    <div class="container">
      <button onclick="displayProjects()">Click to Select Projects</button>
      <p id="tip"></p>
      <select id="projectSelect" multiple="true"></select>
      <div id="submit"></div><p id="submitText" style="font-size: small"></p>
      <p></p>
      <script>
        function displayProjects() {
          document.getElementById("tip").innerHTML = "Hold down 'ctrl' to select multiple projects.";
          var select = document.getElementById("projectSelect");
          var projects = [
            "Example Project 1",
            "Example Project 2",
            "Example Project 3",
            "Example Project 4"
          ];

          select.innerHTML = "";
          for (var i = 0; i < projects.length; i++) {
            var option = projects[i];
            select.innerHTML += "<option>" + option + "</option>";
          }
          var submit = document.getElementById("submit");
          submit.innerHTML = "<button onclick=\"submitProjects()\">Submit</button>";
        }
        function submitProjects() {
          var submitText = document.getElementById("submitText");
          submitText.innerHTML = "<i>Submitted.</i>"
        }
      </script>
    </div>
    <div class="container">
      <button onclick="displaySnapshots()">Click to Display snapshots</button>
      <p id="title"></p>
      <div id="table"></div>
      <script>
        function displaySnapshots() {
          var title = "<h2>Snapshots</h2>";
          document.getElementById("title").innerHTML = title;
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
        }
      </script>
    </div>
  </body>
</html>