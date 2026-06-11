<?php

namespace App\Console\Commands;

use App\Models\Technical;
use Carbon\Carbon;
use Illuminate\Console\Command;
use Google_Client;

use Google_Service_Datastore;
use Google_Service_Datastore_Query;
use Google_Service_Datastore_KindExpression;
use Google_Service_Datastore_PropertyOrder;
use Google_Service_Datastore_PropertyReference;
use Google_Service_Datastore_RunQueryRequest;

class ImportTechnicalFromDataStore extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'import:technical';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'This will export all technical data from technical app in datastore';

    /**
     * Execute the console command.
     */
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
        $kind->setName('Intervention');
        $query->setKind($kind);
        $order = new Google_Service_Datastore_PropertyOrder();
        $order->setProperty(new Google_Service_Datastore_PropertyReference(['name' => 'interventionDate']));
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
                $intervention_date = $this->getProperty($entity, "interventionDate", "string");
                echo($index++. ' : '.$site.":". $intervention_date."\n");
                if($site != null && $site != "") {
                    Technical::create([  
                        'site' => $this->getProperty($entity, "site", "string"),
                        'acknowledge_time' => $this->getProperty($entity, "acknowledge_time", "timestamp"),
                        'request_item_email' => $this->getProperty($entity, "amount", "float"),
                        'validated_item_email' => $this->getProperty($entity, "amount_riel", "float"),
                        'stop_work' => $this->getProperty($entity, "stop_work", "float"),
                        'charge_from' => $this->getProperty($entity, "charge_from", "string"),
                        'technician' => $this->getProperty($entity, "technician", "string"),
                        'technician2' => $this->getProperty($entity, "technician2", "string"),
                        'rt_comment' => $this->getProperty($entity, "comment", "string"),
                        'comment_other' => $this->getProperty($entity, "comment_other", "string"),
                        'comment_problem' => $this->getProperty($entity, "comment_problem", "string"),
                        'creation_date' => $this->getProperty($entity, "creation_date", "timestamp"),
                        'distance' => $this->getProperty($entity, "distance", "float"),
                        'email_quotation' => $this->getProperty($entity, "email_quotation", "string"),
                        'end_point' => $this->getProperty($entity, "end_point", "string"),
                        'start_point' => $this->getProperty($entity, "start_point", "string"),
                        'entrepreneur_pay' => $this->getProperty($entity, "entrepreneur_pay", "string"),
                        'Fixed' => $this->getProperty($entity, "Fixed", "string"),
                        'gasoline' => $this->getProperty($entity, "gasoline", "float"),
                        'problem_date' => $this->getProperty($entity, "interventionDate", "timestamp"),
                        'stop' => $this->getProperty($entity, "stop", "timestamp"),
                        'end_intervention' => $this->getProperty($entity, "start", "timestamp"),
                        'last_update' => $this->getProperty($entity, "last_update", "timestamp"),
                        'date_need' => $this->getProperty($entity, "date_need", "timestamp"),
                        'phone_number' => $this->getProperty($entity, "phone_number", "string"),
                        'item_receiver' => $this->getProperty($entity, "item_receiver", "string"),
                        'stock_type' => $this->getProperty($entity, "stock_type", "string"),
                        'rt_request_stock' => $this->getProperty($entity, "validated_item", "string"),
                        'start_intervention' => $this->getProperty($entity, "plan_date", "timestamp"),
                        'price_gasoline' => $this->getProperty($entity, "price_gasoline", "float"),
                        'problem_status' => $this->getProperty($entity, "problem_status", "string"),
                        'status' => $this->getProperty($entity, "status", "string"),
                        'quotation' => $this->getProperty($entity, "quotation", "string"),
                        'report_by' => $this->getProperty($entity, "report_by", "string"),
                        'reporting' => $this->getProperty($entity, "reporting", "string"),
                        'rt_advisor' => $this->getProperty($entity, "rt_advisor", "string"),
                        'rt_site_problem_description' => $this->getProperty($entity, "rt_site_problem_description", "string"),
                        'site_problem_description' => $this->getProperty($entity, "site_problem_description", "string"),
                        'rt_sub_problem_description' => $this->getProperty($entity, "rt_sub_problem_description", "string"),
                        'sub_problem_description' => $this->getProperty($entity, "sub_problem_description", "string"),
                        'send_quotation' => $this->getProperty($entity, "send_quotation", "string"),
                        'site_platform' => $this->getProperty($entity, "site_platform", "string"),
                        'rt_solution' => $this->getProperty($entity, "rt_solution", "string"),
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
