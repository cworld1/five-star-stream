class WebServer:
    def print_server_link(port):
        print(f"网页版播放器链接: http://localhost:{port}/")

    def send_static_html(handler):
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html")
        handler.end_headers()
        html_content = """
<!DOCTYPE html>
<html lang="zh">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>M3U8 播放器</title>
    <meta name="color-scheme" content="light dark" />
    <style>
      body {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        margin: 0;
      }
      main {
        width: 80%;
        max-width: 800px;
      }
      video {
        width: 100%;
        border: 1px solid #8e8e8e80;
      }
      .input-container {
        display: flex;
        column-gap: 10px;
        margin-top: 20px;
      }
      input {
        flex: 1;
        padding: 10px 15px;
      }
      button {
        padding: 10px 20px;
        cursor: pointer;
      }
      .desc {
        color: #68686b;
      }
      @media (prefers-color-scheme: dark) {
        .desc {
          color: #b8b8c3;
        }
      }
      @media (max-width: 600px) {
        main {
          width: 100%;
          padding: 10px;
        }
        input,
        button {
          padding: 7px 10px;
        }
      }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
  </head>
  <body>
    <main>
      <h1>M3U8 播放器</h1>
      <video id="videoPlayer" controls></video>
      <div class="input-container">
        <input type="text" id="m3u8Input" placeholder="请输入M3U8链接" />
        <button id="playButton">播放视频</button>
      </div>
      <p class="desc">空格键播放/暂停；方向键控制音量/进度；双击窗口全屏</p>
    </main>

    <script>
      const videoPlayer = document.getElementById("videoPlayer");

      document
        .getElementById("playButton")
        .addEventListener("click", function () {
          const m3u8Url = document.getElementById("m3u8Input").value;

          if (Hls.isSupported()) {
            const hls = new Hls();
            hls.loadSource(m3u8Url);
            hls.attachMedia(videoPlayer);
            hls.on(Hls.Events.MANIFEST_PARSED, function () {
              videoPlayer.play();
            });
          } else if (videoPlayer.canPlayType("application/vnd.apple.mpegurl")) {
            videoPlayer.src = m3u8Url;
            videoPlayer.addEventListener("loadedmetadata", function () {
              videoPlayer.play();
            });
          } else {
            alert("该浏览器不支持播放 M3U8 格式的视频。");
          }
        });

      // 全屏播放
      videoPlayer.addEventListener("dblclick", function () {
        if (videoPlayer.requestFullscreen) {
          videoPlayer.requestFullscreen();
        } else if (videoPlayer.mozRequestFullScreen) {
          // Firefox
          videoPlayer.mozRequestFullScreen();
        } else if (videoPlayer.webkitRequestFullscreen) {
          // Chrome, Safari and Opera
          videoPlayer.webkitRequestFullscreen();
        } else if (videoPlayer.msRequestFullscreen) {
          // IE/Edge
          videoPlayer.msRequestFullscreen();
        }
      });

      // 键盘控制
      document.addEventListener("keydown", function (event) {
        switch (event.code) {
          case "Space":
            event.preventDefault(); // 防止页面滚动
            if (videoPlayer.paused) {
              videoPlayer.play();
            } else {
              videoPlayer.pause();
            }
            break;
          case "ArrowUp":
            videoPlayer.volume = Math.min(videoPlayer.volume + 0.1, 1);
            break;
          case "ArrowDown":
            videoPlayer.volume = Math.max(videoPlayer.volume - 0.1, 0);
            break;
          case "ArrowRight":
            videoPlayer.currentTime = Math.min(
              videoPlayer.currentTime + 10,
              videoPlayer.duration
            );
            break;
          case "ArrowLeft":
            videoPlayer.currentTime = Math.max(videoPlayer.currentTime - 10, 0);
            break;
        }
      });
    </script>
  </body>
</html>
          """
        handler.wfile.write(html_content.encode("utf-8"))
