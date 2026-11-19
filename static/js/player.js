(() => {
  const video = document.getElementById("saki-player");
  if (!video) return;
  const src = video.dataset.src;
  const error = document.getElementById("player-error");
  const isHls = /\\.m3u8($|[?#])/i.test(src);
  let hls;
  if (isHls && window.Hls && Hls.isSupported()) {
    hls = new Hls();
    hls.loadSource(src); hls.attachMedia(video);
    hls.on(Hls.Events.ERROR, (_, data) => { if (data.fatal) error.classList.remove("hidden"); });
  } else if (isHls && video.canPlayType("application/vnd.apple.mpegurl")) {
    video.src = src;
  } else {
    video.src = src;
  }
  video.addEventListener("error", () => error.classList.remove("hidden"));
  const progressKey = "saki-progress";
  const id = video.dataset.episode;
  let progress = {};
  try { progress = JSON.parse(localStorage.getItem(progressKey) || "{}"); } catch {}
  const saved = progress[id];
  if (saved && saved.time > 5) video.addEventListener("loadedmetadata", () => {
    if (Number.isFinite(video.duration) && saved.time < video.duration - 5) video.currentTime = saved.time;
  }, {once:true});
  let lastSave = 0;
  video.addEventListener("timeupdate", () => {
    if (Date.now() - lastSave < 4000) return;
    lastSave = Date.now();
    const duration = video.duration || 0;
    progress[id] = {
      time: video.currentTime,
      percent: duration ? video.currentTime / duration * 100 : 0,
      title: document.title.split(" — ")[0],
      poster: video.poster,
      url: location.pathname
    };
    localStorage.setItem(progressKey, JSON.stringify(progress));
  });
  video.addEventListener("ended", () => {
    delete progress[id]; localStorage.setItem(progressKey, JSON.stringify(progress));
  });
  window.addEventListener("beforeunload", () => {
    if (video.currentTime > 0) {
      progress[id] = {time:video.currentTime, percent:video.duration ? video.currentTime/video.duration*100 : 0, title:document.title.split(" — ")[0], poster:video.poster, url:location.pathname};
      localStorage.setItem(progressKey, JSON.stringify(progress));
    }
  });
})();