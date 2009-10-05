<?php
function getcontype($where)
{
$db = sqlite3_open("/home/tom/sf/new.db");
if (!$db) die ("Could open database..");

$query = sqlite3_query($db, "SELECT * FROM pers WHERE id IN (SELECT pid FROM contr WHERE $where) ORDER BY lname");
if (!$query) die (sqlite3_error($db));

while ( ($pers = sqlite3_fetch_array($query)))
{
        $query2 = sqlite3_query($db, "SELECT * FROM contr WHERE $where AND pid=".$pers['id']);
        if (!$query2) die (sqlite3_error($db));

        while ( ($contr = sqlite3_fetch_array($query2)))
         {
          printf("<li><a name=\"c%s\" /><strong>%s %s</strong><br /><strong>Title:</strong> %s<br /><strong>File:</strong> <a href=\"http://star-forming-dwarfs.org/files/%s\">%s</a><br /><strong>Abstract:</strong> %s</li>\n", $contr['id'],$pers['fname'], $pers['lname'],$contr['title'],$contr['filename'],$contr['filename'],$contr['abstract']);
         }
        sqlite3_query_close($query2);
}
sqlite3_query_close($query);
sqlite3_close ($db);
}
?>
<p>Links to scroll down to...
<ul>
<li><a href="#talks">... talks</a></li>
<li><a href="#posters">... posters</a></li>
<li><a href="#demos">... practical demonstrations</a></li>
<li><a href="#discuss">... discussion sessions</a></li>
</ul>

<a name="talks" />
<h2>Talks</h2>
<p>
<ul>
<?php getcontype('type=1'); ?>
</ul></p>

<a name="posters" />
<h2>Posters</h2>
<p>
<ul>
<?php getcontype('type=2'); ?>
</ul>
</p>

<a name="demos" />
<h2>Practical demonstrations: data analysis & visualisation</h2>
<p>
This part of the list will be completed soon. If you have a good tool or software that you want to show, you can still <a href="/abstract.html">submit</a> a short contribution to the demonstration session.
<ul>
<?php getcontype('type=4'); ?>
</ul>
</p>

<a name="discuss" />
<h2>Discussion Sessions</h2>
<p>
More detailed information follows.
<ul>
<?php getcontype('type=5'); ?>
</ul>
</p>
