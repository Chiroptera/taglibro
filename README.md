App for journaling.

TODO features:
 - organize files in folders
 - journal encryption
 - integration with storage services (start with Dropbox but leave groundwork for others)
 - configuration file
 - migrate the whole thing to Python 3

TODO webapp:
 - database with all tags
 - tag completion

Dependencies:
 - pandoc
 - pypandoc
 - argparse

 {{ for entry in entries }}
         <div id="entry">
           <div id="entry_header">
             <dl class="dl-horizontal">
               <dt>date</dt>
               <dd>{{ entry['header']['date'] }}</dd>
               <dt>tag</dt>
               <dd>{{ entry['header']['tags'] }}</dd>
             </dl>
           </div> <!-- entry header -->
           <div id="entry_body">
             {{ entry['body'] }}
           </div> <!-- entry header -->
           <hr></hr>
         </div> <!-- entry -->
 {{ end for }}
