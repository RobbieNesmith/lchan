function createBoard(title, route)
{
  var data = {};
  data.title = title;
  data.route = route;
  
  var string = JSON.stringify(data);
  
  xhr = new XMLHttpRequest();
  xhr.open("POST", "/api/add/board");
  xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
  
  xhr.onreadystatechange = function()
  {
    if(xhr.readyState == 4)
    {
      errormessage = document.getElementById("errormessage");
      resp = JSON.parse(xhr.responseText);
      if(xhr.status == 200 && resp.error == null)
      {
        postContainer = document.getElementById("postcontainer");
        newpost = document.createElement("a");
        newpost.className = "list-group-item mylistitem";
        newpost.href = "/boards/" + route;
        newpost.innerHTML = title;
        npbadge = document.createElement("span");
        npbadge.className = "badge";
        npbadge.innerHTML = "0";
        newpost.appendChild(npbadge);
        postContainer.insertBefore(newpost,postContainer.firstChild);
        errormessage.innerHTML = "";
      }
      else
      {
        errormessage.innerHTML = resp.error;
      }
    }
  };
  xhr.send(string);
}

function createThread(board, title, message)
{
  var data = {};
  data.board = board;
  data.title = title;
  data.message = message;
  
  var string = JSON.stringify(data);
  
  xhr = new XMLHttpRequest();
  xhr.open("POST", "/api/add/thread");
  xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
  
  xhr.onreadystatechange = function()
  {
    if(xhr.readyState == 4)
    {
      errormessage = document.getElementById("errormessage");
      resp = JSON.parse(xhr.responseText);
      if(xhr.status == 200 && resp.error == null)
      {
        postContainer = document.getElementById("postcontainer");
        newpost = document.createElement("a");
        newpost.className = "list-group-item mylistitem";
        newpost.href = "/threads/" + resp.thread;
        newpost.innerHTML = title;
        npbadge = document.createElement("span");
        npbadge.className = "badge";
        npbadge.innerHTML = "1";
        newpost.appendChild(npbadge);
        postContainer.insertBefore(newpost,postContainer.firstChild);
        errormessage.innerHTML = "";
        title = document.getElementById("title");
        message = document.getElementById("message");
        title.value = ""
        message.value = ""
      }
      else
      {
        errormessage.innerHTML = resp.error;
      }
    }
  };
  xhr.send(string);
}

function createPost(thread, title, message)
{
  var data = {};
  data.thread = thread;
  data.title = title;
  data.message = message;
  
  var string = JSON.stringify(data);
  
  xhr = new XMLHttpRequest();
  xhr.open("POST", "/api/add/post");
  xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
  
  xhr.onreadystatechange = function()
  {
    if(xhr.readyState == 4)
    {
      errormessage = document.getElementById("errormessage");
      resp = JSON.parse(xhr.responseText);
      if(xhr.status == 200 && resp.error == null)
      {
        postContainer = document.getElementById("postcontainer");
        newpost = document.createElement("li");
        newpost.className = "list-group-item mylistitem";
        newpost.innerHTML = "<h3>" + title + " - <small>(" + resp.username + ")</small></h3><br />" + message;
        postContainer.insertBefore(newpost,postContainer.firstChild);
        errormessage.innerHTML = "";
        title = document.getElementById("title");
        message = document.getElementById("message");
        title.value = ""
        message.value = ""
      }
      else
      {
        errormessage.innerHTML = resp.error;
      }
    }
  };
  xhr.send(string);
}