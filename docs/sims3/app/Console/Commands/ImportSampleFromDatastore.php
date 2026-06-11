<?php

namespace App\Console\Commands;

use App\Models\Sample;
use Carbon\Carbon;
use Google_Client;
use Illuminate\Console\Command;
use Google_Service_Datastore;
use Google_Service_Datastore_Query;
use Google_Service_Datastore_KindExpression;
use Google_Service_Datastore_PropertyOrder;
use Google_Service_Datastore_PropertyReference;
use Google_Service_Datastore_RunQueryRequest;

class ImportSampleFromDatastore extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'import:samples';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Import samples from datastore to database';

    public function getProperty($entity, $property, $type) {
        if(!isset($entity[$property])) {
            return null;
        }
        switch($type) {
            case 'string':
                $value = $entity[$property]->getStringValue();
                if($value === "" || $value === null) {
                    return null;
                }
                return $value;
            case 'int':
                $value = $entity[$property]->getStringValue();
                if($value === "" || $value === null) {
                    return null;
                }
                return intval($value);
            case 'float':
                $value = $entity[$property]->getStringValue();
                if($value === "" || $value === null) {
                    return null;
                }
                return floatval($value);
            case 'timestamp':
                $value = $entity[$property]->getTimestampValue();
                if($value === "" || $value === null) {
                    return null;
                }
                return Carbon::parse($value);
        }
    }

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $projectId = "sims-2-140009";
        putenv('GOOGLE_APPLICATION_CREDENTIALS=' . storage_path('app/client_secret_appengine.json'));

        $client = new Google_Client();
        $client->useApplicationDefaultCredentials();
        $client->addScope('https://www.googleapis.com/auth/cloud-platform');
        $datastore = new Google_Service_Datastore($client);
        $query = new Google_Service_Datastore_Query();
        $kind = new Google_Service_Datastore_KindExpression();
        $kind->setName('Sample');
        $query->setKind($kind);
        $order = new Google_Service_Datastore_PropertyOrder();
        $order->setProperty(new Google_Service_Datastore_PropertyReference(['name' => 'analysisDate']));
        $order->setDirection('DESCENDING');
        $query->setOrder([$order]);
        $query->setLimit(300);

        // Execute the query
        $request = new Google_Service_Datastore_RunQueryRequest(['query' => $query]);
        $response = $datastore->projects->runQuery($projectId, $request);
        $hasMoreResult = true;
        $index = 0;
        
        // Process the response
        while ($hasMoreResult) {
            $entities = $response->getBatch()->getEntityResults();
            $hasMoreResult = $response->getBatch()->getMoreResults() == "MORE_RESULTS_AFTER_LIMIT";
            foreach ($entities as $entityResult) {
                $entity = $entityResult->getEntity()->getProperties();
                $site = $this->getProperty($entity, "site", "string");
                $sample_date = $this->getProperty($entity, "stringSampleDate", "string");
                echo($index++. ' : '.$site.":". $sample_date."\n");
                if($site != null && $site != "") {
                    Sample::create([
                        'action_done' => strtolower($this->getProperty($entity, "actionDone", "string")) === "yes" ? 1 : 0,
                        'alert_number' => $this->getProperty($entity, "alert_number", "string"),
                        'alkalinity' => $this->getProperty($entity, "alkalinity", "string"),
                        'aluminium' => $this->getProperty($entity, "aluminium", "string"),
                        'amonia' => $this->getProperty($entity, "amonia", "string"),
                        'analysis_date' => $this->getProperty($entity, "analysisDate", "timestamp"),
                        'arsenic' => $this->getProperty($entity, "arsenic", "string"),
                        'calcium' => $this->getProperty($entity, "calcium", "string"),
                        'chloride' => $this->getProperty($entity, "chloride", "string"),
                        'chlorine' => $this->getProperty($entity, "chlorine", "string"),
                        'color' => $this->getProperty($entity, "color", "string"),
                        'comment' => $this->getProperty($entity, "comment", "string"),
                        'conductivity' => $this->getProperty($entity, "conductivity", "string"),
                        'contamination_level_bottle' => $this->getProperty($entity, "contaminationLevelBottle", "int"),
                        'contamination_level_machine' => $this->getProperty($entity, "contaminationLevelMachine", "int"),
                        'created_by' => $this->getProperty($entity, "createdBy", "string"),
                        'delay' => $this->getProperty($entity, "delay", "int"),
                        'desinfection' => $this->getProperty($entity, "desinfection", "string"),
                        'email_alert' => $this->getProperty($entity, "email_alert", "string") === "yes" ? 1 : 0,
                        'escherichia' => $this->getProperty($entity, "escherichia", "string"),
                        'escherichia_bottle' => $this->getProperty($entity, "escherichiaBottle", "string"),
                        'fluoride' => $this->getProperty($entity, "fluoride", "string"),
                        'hardness' => $this->getProperty($entity, "hardness", "string"),
                        'iron' => $this->getProperty($entity, "iron", "string"),
                        'last_updates' => $this->getProperty($entity, "lastUpdates", "string"),
                        'manganese' => $this->getProperty($entity, "manganese", "string"),
                        'nitrate' => $this->getProperty($entity, "nitrate", "string"),
                        'nitrite' => $this->getProperty($entity, "nitrite", "string"),
                        'ph' => $this->getProperty($entity, "ph", "string"),
                        'pretreatment' => $this->getProperty($entity, "pretreatment", "string"),
                        'production' => $this->getProperty($entity, "production", "string"),
                        'received_date' => $this->getProperty($entity, "recievedDate", "timestamp"),
                        'response_date' => $this->getProperty($entity, "responseDate", "timestamp"),
                        'root_cause' => $this->getProperty($entity, "rootCause", "string"),
                        'safe' => $this->getProperty($entity, "safe", "string"),
                        'sample_date' => $this->getProperty($entity, "sampleDate", "timestamp"),
                        'silver' => $this->getProperty($entity, "silver", "string"),
                        'site' => $this->getProperty($entity, "site", "string"),
                        'smell' => $this->getProperty($entity, "smell", "string"),
                        'sulfates' => $this->getProperty($entity, "sulfates", "string"),
                        'taste' => $this->getProperty($entity, "taste", "string"),
                        'tds' => $this->getProperty($entity, "tds", "string"),
                        'temperature' => $this->getProperty($entity, "temperature", "string"),
                        'test_number' => $this->getProperty($entity, "test_number", "string"),
                        'total_coliform' => $this->getProperty($entity, "totalColiform", "string"),
                        'total_coliform_bottle' => $this->getProperty($entity, "totalColiformBottle", "string"),
                        'total_chlore' => $this->getProperty($entity, "totalchlore", "string"),
                        'turbidity' => $this->getProperty($entity, "turbidity", "string"),
                    ]);
                } else {
                    echo(" IGNORED \n");
                }
            }
            $query->startCursor = $response->getBatch()->getEndCursor();
            $response = $datastore->projects->runQuery($projectId, $request);
        }
    }
}
