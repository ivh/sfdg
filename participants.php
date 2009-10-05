<p>
<ul>
<?php

$db = sqlite3_open("/home/tom/sf/new.db");
if (!$db) die ("Could open database..");

$query = sqlite3_query($db, "SELECT * FROM pers WHERE id!=43 AND id!=45 ORDER BY lname");
if (!$query) die (sqlite3_error($db));


while ( ($row = sqlite3_fetch_array($query)))
{
        printf("<li>%s %s, %s</li>\n", $row['fname'], $row['lname'],$row['affil']);
}


sqlite3_query_close($query);
sqlite3_close ($db);

?>
</ul>
</p>
