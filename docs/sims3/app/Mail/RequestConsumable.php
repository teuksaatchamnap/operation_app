<?php

namespace App\Mail;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class RequestConsumable extends Mailable
{
    use Queueable, SerializesModels;
    public $items;
    /**
     * Create a new message instance.
     */
    public function __construct($item)
    {
        $this->items = $item;
       
    }

    /**
     * Get the message envelope.
     */
    public function envelope(): Envelope
    {
        
        return new Envelope(
            subject: 'Request Consumable Approval',
        );
    }

    /**
     * Get the message content definition.
     */
    public function content(): Content
    {
        $amount= 0;
        $amount = $this->items['totalQty']/4000;
        if ($amount > 300 ) {
            return new Content(
                markdown: 'emails.RequestConsumable.MDvalidate',
            );
        } else {
            return new Content(
                markdown: 'emails.RequestConsumable.managerValidate',
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
        return [];
    }
}
