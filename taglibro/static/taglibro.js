var entries = null;

function get_date(){
  var now = new Date();
  var date_str = '';
  if (now.getDate() < 10) date_str += '0';
  date_str += now.getDate();
  date_str += '-';

  if (now.getMonth() + 1 < 10) date_str += '0';
  date_str += now.getMonth() + 1;
  date_str += '-';

  date_str += now.getFullYear();
  date_str += ' ';

  if (now.getHours() < 10) date_str += '0';
  date_str += now.getHours();
  date_str += ':';

  if (now.getMinutes() < 10) date_str += '0';
  date_str += now.getMinutes();

  return date_str;
}

function render_entry(entry){
  var html = '<div>';
  // header
  html += '<div>';
  html += '<dl class="dl-horizontal">';
  html += '<dt> date </dt> <dd>' + entry.header.date + '</dd>';
  html += '<dt> tag </dt> <dd>' + entry.header.tags + '</dd>';
  html += '</dl>';
  html += '</div>';  //end of header
  // body
  html += '<div>';
  html += entry.body.markdown;
  html += '</div>';  //end of body

  html += '</div>';  //end of entry

  return html;
}

function new_entry(){
  var gen_entry = {
    'header': {
      'date': get_date(),
      'tags': []
    },
    'body': {
      'markdown': '',
      'txt': ''
    }
  };
  return gen_entry;
}

function raw_entry_to_send(e){
  var raw = '---\n';
  raw += 'date: ' + e.header.date + '\n';
  raw += 'tag: ' + e.header.tags + '\n';
  raw += '---\n\n';
  raw += e.body.txt;
  return raw;
}

function save(e){

  var entry_txt = raw_entry_to_send(e) ;
  var payload = { body: raw_entry_to_send(e) };
  console.log(entry_txt);
  console.log(payload);

  $.ajax({
    url:"entry",
    type:"POST",
    data:JSON.stringify(payload),
    contentType:"application/json; charset=utf-8",
    dataType:"json",
    success: null
  })
}

function save_entry(e){
  $.ajax({
    url:"entry",
    type:"POST",
    data:JSON.stringify(e),
    contentType:"application/json; charset=utf-8",
    dataType:"json",
    success: null
  })
}

var edit_html = '<div id="editor_col" class="col-md-6">';
edit_html += '<textarea id="editor" class="field span12" rows=20 placeholder="taglibro"></textarea>';
edit_html += '<p><button id="btnSave" type="button" class="btn btn-primary btn-lg">Save</button></p>';
edit_html += '</div>';

// function clear(){
//   console.log('clear');
//   //$('#editor').text('---\n---');
// }

function editor_render_entry(e){
  $('#date').text(' ' + e.header.date);
  $('#tags').val(e.header.tags);
  $('#editor').val(e.body.txt);
}

$( document ).ready(function(){
  var entry_in_edit = new_entry();
  editor_render_entry(entry_in_edit);

  // requesting entries from backend
  $.get("entry", function( data ) {
    entries = data;
    //alert( "Got entries." );
    console.log(data);

    console.log('looping entries');
    for(var i=0; i < entries.length; i++){
        html = render_entry(entries[i]);
        $('#entry_list').append(html);
    }

  });

  $('#btnSave').click(function(){
    entry_in_edit.body.txt = $('#editor')[0].value;
    entry_in_edit.header.tags = $('#tags')[0].value;
    save(entry_in_edit);
    // save_entry();
  });

});
