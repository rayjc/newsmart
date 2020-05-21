$(async function(){
  const $topDiv = $('#top-articles');
  const $categoryDiv = $('#category-articles');
  const $relatedDiv = $('#related-articles');
  const $searchDiv = $('#search-articles');
  const newsmart = new NewSmartSession();

  console.log("CONNECTED");

  $topDiv.on("click", "button.btn-bookmark", bookmarkHandler);
  $categoryDiv.on("click", "button.btn-bookmark", bookmarkHandler);
  $relatedDiv.on("click", "button.btn-bookmark", bookmarkHandler);
  $searchDiv.on("click", "button.btn-bookmark", bookmarkHandler);


  async function bookmarkHandler(event) {
    console.log("clicked a top article.")

    const $this = $(this);
    $this.empty();    // remove bookmark icon
    const hasBookmarked = $this.attr('data-bookmark-id');
    if (typeof hasBookmarked !== typeof undefined && hasBookmarked !== false) {
      const bookmark = await newsmart.removeBookmark($this.attr('data-bookmark-id'));

      $this.removeAttr('data-bookmark-id').append('<i class="far fa-bookmark"></i>');
    } else {
      const $article = $this.parent();
      const bookmark = await addBookmark(
        $article.attr('data-title'), $article.attr('data-summary'),
        $article.attr('data-content'), $article.attr('data-url'),
        $article.attr('data-img-url'), $article.attr('data-source'),
        $article.attr('data-timestamp')
      );

      $this.attr('data-bookmark-id', bookmark.id).append('<i class="fas fa-bookmark"></i>');
    }
  }

  async function addArticleAndTags(title, summary, content, url, img_url, source, timestamp) {
    const savedArticle = await newsmart.getArticle(url);
    // check if article url exists in db
    if (!savedArticle) {
      // save article
      const articleRequest = newsmart.saveArticle(
        title, summary, content, url, img_url, source, timestamp
      );

      // extract and save tags
      const tagsRequest = newsmart.saveTags(url);

      // join the two requests
      const [article, tags] = await Promise.all([articleRequest, tagsRequest]);

      // create article-tag associations
      for (const tag of tags) {
        await newsmart.saveArticleTagLink(article.id, tag.id);
      }
      
      return article;
    }

    return savedArticle;
  }

  async function addBookmark(title, summary, content, url, img_url, source, timestamp) {
    const savedArticle = await addArticleAndTags(
      title, summary, content, url, img_url, source, timestamp
    );

    // save bookmark
    const bookmark = await newsmart.saveBookmark(savedArticle.id);
    return bookmark;
  }

});