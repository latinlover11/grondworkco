// Redirect www to the apex. Every canonical, sitemap entry and og:url on the
// site names https://waxwinglandscaping.com, so www is a duplicate hostname and
// should hand off rather than serve. Path and query string are preserved.
export default {
  async fetch(request) {
    const url = new URL(request.url);
    return Response.redirect("https://waxwinglandscaping.com" + url.pathname + url.search, 301);
  },
};
