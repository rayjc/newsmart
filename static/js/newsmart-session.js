class NewSmart {
  constructor() {
    this.articlesUrl = "/api/articles";
    this.savesUrl = "/api/saves";
    this.tagsUrl = "/api/tags";
    this.articleTagUrl = "/api/articletag";
    this.userCategoryUrl = "/api/usercategory"
  }

  async getArticle(url) {
    try {
      const response = await axios.get(this.articlesUrl,
        {
          params: {article_url: url},
          validateStatus: function (status) {
            return status < 500; // Resolve only if the status code is less than 500
          }
        }
      );
      return response.data.article;
    } catch (error) {
      axiosErrorHandler(error);
    }
    return null;
  }

  async saveArticle(title, summary, content, url, img_url, source, timestamp) {
    try {
      const response = await axios.post(this.articlesUrl, {
        title, summary, content, url, img_url, source, timestamp,
      });
      return response.data.article;
    } catch (error) {
      axiosErrorHandler(error);
    }
    return null;
  }

  async saveBookmark(articleId) {
    try {
      const response = await axios.post(this.savesUrl, {article_id: articleId});
      return response.data.bookmark;
    } catch (error) {
      axiosErrorHandler(error);
    }
    return null;
  }

  async removeBookmark(bookmarkId) {
    try {
      const response = await axios.delete(`${this.savesUrl}/${bookmarkId}`);
      return response.data.bookmark;
    } catch (error) {
      axiosErrorHandler(error);
    }
    return null;
  }

  async saveTags(articleUrl) {
    try {
      const response = await axios.post(this.tagsUrl, { article_url: articleUrl });
      return response.data.tags;
    } catch (error) {
      axiosErrorHandler(error);
    }
    return null;
  }

  async saveArticleTagLink(articleId, tagId) {
    try {
      const response = await axios.post(this.articleTagUrl,{
        article_id: articleId,
        tag_id: tagId
      });
      return response.data.articletag;
    } catch (error) {
      axiosErrorHandler(error);
    }
    return null;
  }

  async updateUserCategories(categoryIds) {
    try {
      const response = await axios.put(this.userCategoryUrl, { category_ids: categoryIds });
      return response.data.users_categories;
    } catch (error) {
      axiosErrorHandler(error);
    }
    return null;
  }
}


function axiosErrorHandler(error) {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    console.log(error.response.data);
    console.log(error.response.status);
    console.log(error.response.headers);
  } else if (error.request) {
    // The request was made but no response was received
    // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
    // http.ClientRequest in node.js
    console.log(error.request);
  } else {
    // Something happened in setting up the request that triggered an Error
    console.log('Error', error.message);
  }
  console.log(error.config);
}
