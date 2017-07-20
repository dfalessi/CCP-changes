<!DOCTYPE html>
<html lang="en">
  <head>
      <title>Bootstrap Test Page 3</title>
      <meta charset="utf-8">
      <meta name="description" content="Testing bootstrap here!">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
      <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
  </head>
  <body>
    <div class="container">
      <button onclick="myFunction()">Try it</button>
      <div id="demo"></div>
      <script>
        function myFunction() {
          var title = "<h2>Snapshot</h2>";
          document.write(title);
          var stats = [
            "Date Created |",
            "Project Name |",
            "Revision",
          ];

          var table = "<table class = \"table table-bordered\"><thead><tr>";
          for (var i = 0; i < stats.length; i++) {
            table += "<th>" + stats[i] + "</th>";
          }
          table += "</tr></thead></table>";
          document.write(table);
        }
      </script>
    </div>
  </body>
</html>