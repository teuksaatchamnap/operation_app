<?php

namespace App\Mail;

use App\Models\Technical;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Attachment;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class RequestTechnicalItem extends Mailable
{
    use Queueable, SerializesModels;

    /**
     * Create a new message instance.
     */
    public function __construct(public Technical $technical)
    {
        //
    }

    /**
     * Get the message envelope.
     */
    public function envelope(): Envelope
    {
        return new Envelope(
            subject: 'Request Technical Item on Site : '. $this->technical->site,
          );
    }

    /**
     * Get the message content definition.
     */
    public function content(): Content
    {
        if ($this->technical->totalPriceAllItem >= 200000)
        {
            return new Content(
                markdown: 'emails.ROMvalidate',
            );
        }
        else
        {
            return new Content(
                markdown: 'emails.request_technical_item',
            );
        }
        
    }

    /**
     * Get the attachments for the message.
     *
     * @return array<int, \Illuminate\Mail\Mailables\Attachment>
     */
    public function attachments(): array
    {
        return[];
        // $path1= public_path('/public/img/analysis.jpeg');
        // $aa=  Attachment::fromStorage('/img/lab.png');
        // dd($aa);
        // return [
        //      Attachment::fromStorage('/img/lab.png')
        // ];

    }
}
