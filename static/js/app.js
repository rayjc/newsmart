$(async function(){
  const $topDiv = $('#top-articles');
  const $categoryDiv = $('#category-articles');
  const $relatedDiv = $('#related-articles');
  const $searchDiv = $('#search-articles');
  const $categoryForm = $('#category-form');
  const $categoryBtn = $('#category-btn')
  const newsmart = new NewSmartSession();

  $topDiv.on("click", "button.btn-bookmark", bookmarkHandler);
  $categoryDiv.on("click", "button.btn-bookmark", bookmarkHandler);
  $relatedDiv.on("click", "button.btn-bookmark", bookmarkHandler);
  $searchDiv.on("click", "button.btn-bookmark", bookmarkHandler);
  $categoryForm.on("submit", putCategoryHandler);
  $categoryForm.on("click", ".category-check", function() {
    // revert submit button back
    $categoryBtn.removeClass('btn-success').addClass('btn-primary');
    // disable unchecked checkboxes if three checkboxes have been checked
    $('.category-check').removeAttr('disabled');
    if ($('.category-check:checked').length >= 3) {
      $('.category-check:not(:checked)').attr('disabled', '');
    }
  });

  async function putCategoryHandler(event) {
    event.preventDefault();

    const $this = $(this);
    const ids = [];
    // extract ids from checked categories
    $this.find('.category-check:checked').each(function () {
      ids.push(Number($(this).attr('data-id')));
    });

    const userCategories = await newsmart.updateUserCategories(ids);

    // change submit button to green
    $categoryBtn.removeClass('btn-primary').addClass('btn-success');
  }

  async function bookmarkHandler(event) {
    const $this = $(this);
    $this.empty();    // remove bookmark icon
    const hasBookmarked = $this.attr('data-bookmark-id');
    if (typeof hasBookmarked !== typeof undefined && hasBookmarked !== false) {
      const bookmark = await newsmart.removeBookmark($this.attr('data-bookmark-id'));
      // update bookmark icon
      $this.removeAttr('data-bookmark-id').append('<i class="far fa-bookmark"></i>');
    } else {
      const $article = $this.parent();
      const bookmark = await addBookmark(
        $article.attr('data-title'), $article.attr('data-summary'),
        $article.attr('data-content'), $article.attr('data-url'),
        $article.attr('data-img-url'), $article.attr('data-source'),
        $article.attr('data-timestamp')
      );
      // update bookmark icon
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