<?php

namespace App\Mail;

use Carbon\Carbon;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;
use Illuminate\Mail\Mailables\Attachment;
class FA extends Mailable
{
    use Queueable, SerializesModels;
    public $data;
    /**
     * Create a new message instance.
     */
    public function __construct($f)
    {
        $this->data= $f;        
    }

    /**
     * Get the message envelope.
     */
    public function envelope(): Envelope
    {
        $today = Carbon::now();  // Get current date and time
        $previousMonth = $today->subMonth();  // Subtract one month
        $previousMonthFormatted = $previousMonth->format('Y-m');
        return new Envelope(
            subject: 'Sale Consolidation Report on '.$previousMonthFormatted,
        );
    }

    /**
     * Get the message content definition.
     */
    public function content(): Content
    {
        return new Content(
            markdown: 'emails.fileAttach',
        );
    }

    /**
     * Get the attachments for the message.
     *
     * @return array<int, \Illuminate\Mail\Mailables\Attachment>
     */
    public function attachments(): array
    {
        $today = Carbon::now();  // Get current date and time
        $previousMonth = $today->subMonth();  // Subtract one month
        $previousMonthFormatted = $previousMonth->format('Y-m');
        return [
            //Attachment::fromData(fn()=> $this->data['excel'],'excel.xlsx')
           // Attachment::fromData(fn () => Excel::raw($this->data['excel'], BaseExcel::XLSX), 'dnTechnical.xlsx'),
            //Attachment::fromStorage(public_path('/img/lab.png'))
           // $this->attach($this->$inputFile);
               // Attachment::fromPath(storage_path('app/templates/dnTechnical.xlsx'))
               Attachment::fromData(fn()=>$this->data, 'Sale Report-'.$previousMonthFormatted.'.xlsx')
               ->withMime('application/excel'),
        ];
    }
}
