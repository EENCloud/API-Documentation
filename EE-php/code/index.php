
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">

    <title>Embed Camera on Webpage in PHP</title>
    <style>
        
        .preview_img {
            width: 320px;
            height: 180px;
        }

        img {
            width: 100%;
            border: grey solid thin;
        }

        body {
          padding-top: 5rem;
        }

        .starter-template {
          padding: 3rem 1.5rem;
          text-align: center;
        }

        .row {
            padding-top: 10px;
            padding-bottom: 20px;
        }

        h2 {
            border-bottom: thick linen solid;
        }


    </style>
</head>
<body>
    <main role="main" class="container-fluid">
        <div class="container-fluid">

            <div class="row">
                <div class="col-9 offset-1"> 

                    <h1>Embedding Eagle Eye Previews in PHP</h1>

                    <p>
                        The above is an example of how you can embed the preview stream of a camera on to your webpage.  This works with a simple PHP page and a jQuery plugin to refresh the images.  Just to illustrate that it is working I have included the loading text at the bottom of the image.  This is something that can be easily removed by setting "debug: false" in the jQuery plugin.
                    </p>

                    <p>
                        This works well for a low traffic site without needed the user to create an account.  Authentication is handled in PHP so there isn't any credentials risk in embedding credentials in the webpage.
                    </p>

                    <p>
                        For higher traffic websites, you would want to cache the images before going to each user to prevent unneccessary load on your webserver.  This code sample does not that have implemented now for brevitity.  It will be updating with that functionality in the future.
                    </p>

                    <p>
                        <h4>Steps to Get Started</h4>
                        
                        <uL>
                            <li>Get the code <a href="https://github.com/mcotton/EE-php"> on Github</a></li>
                            <li>On this page, replace "camera_id" with ESN of the actual camera</li>
                            <li>In config.php, put in your credentials for username and password</li>
                        </uL>
                    </p>
                </div>
            
            </div>

            <div class="row">
                <div class="col-9 offset-1"> 
                    <div id="preview"></div> 
                </div>
            </div>
            
        </div>

    </main>

<script src="https://code.jquery.com/jquery-3.3.1.min.js" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>

<script src="jquery.preview.js"></script>
<script>
    $(document).ready(function() {
        $('#preview').cameraPreview({ 'camera_id': '100d93f9', 'width': 640, 'height': 360, 'delay': 1000, 'debug': true });
    });
</script>
</body>
</html>
