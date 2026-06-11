<?php

namespace App\Console\Commands;

use App\Models\Mission;
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

class ImportMissionFromDatastore extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'import:missions';

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
            case 'double':
                $value = $entity[$property]->getDoubleValue();
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
        $kind->setName('Mission');
        $query->setKind($kind);
        $order = new Google_Service_Datastore_PropertyOrder();
        $order->setProperty(new Google_Service_Datastore_PropertyReference(['name' => 'startDate']));
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
                echo($index++. ' : '.$this->getProperty($entity, 'startDate', 'timestamp')."\n");
                Mission::create([
                    'admin_comment' => $this->getProperty($entity, 'admin_comment', 'string'),
                    'cost_accomodation' => $this->getProperty($entity, 'cost_accomodation', 'double'),
                    'cost_gasoline' => $this->getProperty($entity, 'cost_gasoline', 'double'),
                    'cost_per_diem' => $this->getProperty($entity, 'cost_per_diem', 'double'),
                    'days_off' => $this->getProperty($entity, 'days_off', 'double'),
                    'distance' => $this->getProperty($entity, 'distance', 'double'),
                    'end_date' => $this->getProperty($entity, 'endDate', 'timestamp'),
                    'liters' => $this->getProperty($entity, 'liters', 'string'),
                    'location' => $this->getProperty($entity, 'location', 'string'),
                    'nb_days' => $this->getProperty($entity, 'nb_days', 'double'),
                    'nb_nights' => $this->getProperty($entity, 'nb_nights', 'double'),
                    'need_advance' => $this->getProperty($entity, 'need_advance', 'string'),
                    'other_expenses' => $this->getProperty($entity, 'other_expenses', 'string'),
                    'other_expenses_total' => $this->getProperty($entity, 'other_expenses_total', 'double'),
                    'position' => $this->getProperty($entity, 'position', 'string'),
                    'purpose' => $this->getProperty($entity, 'purpose', 'string'),
                    'requester' => $this->getProperty($entity, 'requester', 'string'),
                    'requester_fullname' => $this->getProperty($entity, 'requester_fullname', 'string'),
                    'start_date' => $this->getProperty($entity, 'startDate', 'timestamp'),
                    'status' => $this->getProperty($entity, 'status', 'string'),
                    'title' => $this->getProperty($entity, 'title', 'string'),
                    'total' => $this->getProperty($entity, 'total', 'double'),
                    'transportation' => $this->getProperty($entity, 'transportation', 'string'),
                    'validator' => $this->getProperty($entity, 'validator', 'string'),
                ]);
                //dd($entity, $this->getProperty($entity, 'cost_accomodation', 'double'));
            }
            $query->startCursor = $response->getBatch()->getEndCursor();
            $response = $datastore->projects->runQuery($projectId, $request);            
        }
    }
}
